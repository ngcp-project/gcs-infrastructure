#!/usr/bin/env python3
"""Bridge XSens ROS topics into gcs-infrastructure telemetry transmission.

This node subscribes to XSens topics published by xsens_mti_driver and maps the
latest values into a Telemetry object that is queued through SendTelemetry.
The VehicleXBee thread launched by LaunchVehicleXBee handles packetization and
XBee transmission to the GCS.
"""

import math
import os
import sys
import time
import threading
from typing import Optional

import rospy
from geometry_msgs.msg import Vector3Stamped
from xsens_mti_driver.msg import XsStatusWord


def _prepend_if_dir(path: str) -> None:
    """Prepend path to sys.path when the directory exists."""
    if os.path.isdir(path) and path not in sys.path:
        sys.path.insert(0, path)


def _bootstrap_import_paths() -> list:
    """Collect and configure local paths for gcs-infrastructure dependencies."""
    candidate_roots = []

    env_root = os.environ.get("GCS_INFRASTRUCTURE_ROOT")
    if env_root:
        candidate_roots.append(os.path.abspath(env_root))

    candidate_roots.append(os.path.abspath(os.getcwd()))

    # Probe script location and ancestors so this works from source and devel wrappers.
    probe = os.path.abspath(os.path.dirname(__file__))
    for _ in range(8):
        candidate_roots.append(probe)
        parent = os.path.dirname(probe)
        if parent == probe:
            break
        probe = parent

    # De-duplicate while preserving order.
    unique_roots = []
    for root in candidate_roots:
        if root not in unique_roots:
            unique_roots.append(root)

    for root in unique_roots:
        _prepend_if_dir(os.path.join(root, "Application"))
        _prepend_if_dir(os.path.join(root, "lib", "gcs-packet"))
        # gcs-packet exposes top-level packages (Telemetry, Command, Enum, PacketLibrary)
        # from within its `Packet/` directory.
        _prepend_if_dir(os.path.join(root, "lib", "gcs-packet", "Packet"))
        _prepend_if_dir(os.path.join(root, "lib", "gcs-packet", "Application"))
        _prepend_if_dir(os.path.join(root, "lib", "xbee-python"))
        _prepend_if_dir(os.path.join(root, "lib", "xbee-python", "src"))

    return unique_roots


ATTEMPTED_ROOTS = _bootstrap_import_paths()


# Import gcs-infrastructure interfaces. Prefer installed packages first.
try:
    from Infrastructure import LaunchVehicleXBee, SendTelemetry
except Exception as exc:
    raise ImportError(
        "Failed to import Infrastructure. Ensure dependencies are available "
        "(git submodule update --init --recursive and pip install -r requirements.txt) "
        "or set GCS_INFRASTRUCTURE_ROOT to your repository path. "
        f"Attempted roots: {ATTEMPTED_ROOTS}"
    ) from exc

try:
    # VehicleXBee imports Telemetry from `Telemetry.Telemetry`, so import it the
    # same way here to ensure `isinstance()` checks pass.
    from Telemetry.Telemetry import Telemetry
except Exception as exc:
    raise ImportError(
        "Telemetry package was not found. Ensure gcs-packet is installed (lib/gcs-packet) "
        "and importable. Expected: Telemetry.Telemetry.Telemetry. "
        f"Attempted roots: {ATTEMPTED_ROOTS}"
    ) from exc


class XsensTelemetryState:
    """Thread-safe container for latest ROS sensor values."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.roll = 0.0
        self.pitch = 0.0
        self.yaw = 0.0
        self.speed = 0.0
        self.latitude = 0.0
        self.longitude = 0.0
        self.altitude = 0.0
        self.vehicle_status = 0

    def update_euler(self, msg: Vector3Stamped) -> None:
        with self._lock:
            self.roll = float(msg.vector.x)
            self.pitch = float(msg.vector.y)
            self.yaw = float(msg.vector.z)

    def update_position(self, msg: Vector3Stamped) -> None:
        with self._lock:
            # positionlla publishes x=lat, y=lon, z=alt
            self.latitude = float(msg.vector.x)
            self.longitude = float(msg.vector.y)
            self.altitude = float(msg.vector.z)

    def update_velocity(self, msg: Vector3Stamped) -> None:
        with self._lock:
            vx = float(msg.vector.x)
            vy = float(msg.vector.y)
            vz = float(msg.vector.z)
            self.speed = math.sqrt((vx ** 2) + (vy ** 2) + (vz ** 2))

    def update_status(self, msg: XsStatusWord) -> None:
        with self._lock:
            # Treat GNSS fix availability as a simple vehicle health/availability bit.
            self.vehicle_status = 1 if bool(msg.gnss_fix) else 0

    def snapshot(self):
        with self._lock:
            return {
                "roll": self.roll,
                "pitch": self.pitch,
                "yaw": self.yaw,
                "speed": self.speed,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "altitude": self.altitude,
                "vehicle_status": self.vehicle_status,
            }


class XsensToGcsBridge:
    """Builds Telemetry packets from latest XSens state and sends them."""

    def __init__(self) -> None:
        self.state = XsensTelemetryState()

        self.send_rate_hz = float(rospy.get_param("~send_rate_hz", 1.0))
        self.battery_life_default = float(rospy.get_param("~battery_life_default", 1.0))
        self.patient_status_default = int(rospy.get_param("~patient_status_default", 0))
        self.message_flag_default = int(rospy.get_param("~message_flag_default", 0))
        self.message_lat_default = float(rospy.get_param("~message_lat_default", 0.0))
        self.message_lon_default = float(rospy.get_param("~message_lon_default", 0.0))

        self.position_topic = rospy.get_param("~position_topic", "filter/positionlla")
        self.euler_topic = rospy.get_param("~euler_topic", "filter/euler")
        self.velocity_topic = rospy.get_param("~velocity_topic", "filter/velocity")
        self.status_topic = rospy.get_param("~status_topic", "status")

        rospy.Subscriber(self.position_topic, Vector3Stamped, self.state.update_position, queue_size=5)
        rospy.Subscriber(self.euler_topic, Vector3Stamped, self.state.update_euler, queue_size=5)
        rospy.Subscriber(self.velocity_topic, Vector3Stamped, self.state.update_velocity, queue_size=5)
        rospy.Subscriber(self.status_topic, XsStatusWord, self.state.update_status, queue_size=5)

        rospy.loginfo("XSens bridge subscribed to topics: position=%s euler=%s velocity=%s status=%s",
                      self.position_topic,
                      self.euler_topic,
                      self.velocity_topic,
                      self.status_topic)

    def _build_telemetry(self) -> Telemetry:
        snap = self.state.snapshot()

        telemetry = Telemetry()
        telemetry.Speed = snap["speed"]
        telemetry.Pitch = snap["pitch"]
        telemetry.Yaw = snap["yaw"]
        telemetry.Roll = snap["roll"]
        telemetry.Altitude = snap["altitude"]
        telemetry.BatteryLife = self.battery_life_default
        telemetry.CurrentPositionX = snap["latitude"]
        telemetry.CurrentPositionY = snap["longitude"]
        telemetry.VehicleStatus = snap["vehicle_status"]
        telemetry.PatientStatus = self.patient_status_default
        telemetry.MessageFlag = self.message_flag_default
        telemetry.MessageLat = self.message_lat_default
        telemetry.MessageLon = self.message_lon_default
        telemetry.LastUpdated = int(time.time())

        return telemetry

    def run(self) -> None:
        if self.send_rate_hz <= 0:
            raise ValueError("send_rate_hz must be > 0")

        period = rospy.Duration(1.0 / self.send_rate_hz)
        while not rospy.is_shutdown():
            telemetry = self._build_telemetry()
            SendTelemetry(telemetry)
            rospy.sleep(period)


def main() -> None:
    rospy.init_node("xsens_to_gcs_bridge")

    xbee_port: Optional[str] = rospy.get_param("~xbee_port", None)
    if not xbee_port:
        rospy.logfatal("Parameter ~xbee_port is required (for example: /dev/ttyUSB0).")
        raise RuntimeError("Missing ~xbee_port")

    rospy.loginfo("Starting VehicleXBee on port %s", xbee_port)
    LaunchVehicleXBee(xbee_port)

    bridge = XsensToGcsBridge()
    bridge.run()


if __name__ == "__main__":
    main()
