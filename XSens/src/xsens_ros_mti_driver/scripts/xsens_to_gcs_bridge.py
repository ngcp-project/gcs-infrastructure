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


# Import gcs-infrastructure interfaces. Prefer installed packages first.
try:
    from Infrastructure import LaunchVehicleXBee, SendTelemetry
except Exception:
    # Fallback for local workspace usage where Application is not installed.
    candidate_roots = []
    env_root = os.environ.get("GCS_INFRASTRUCTURE_ROOT")
    if env_root:
        candidate_roots.append(env_root)

    candidate_roots.append(os.getcwd())
    candidate_roots.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../")))

    for root in candidate_roots:
        application_path = os.path.join(root, "Application")
        if os.path.isdir(application_path) and application_path not in sys.path:
            sys.path.insert(0, application_path)

    try:
        from Infrastructure import LaunchVehicleXBee, SendTelemetry
    except Exception as exc:
        raise ImportError(
            "Infrastructure package was not found. Install gcs-infrastructure, "
            "or set GCS_INFRASTRUCTURE_ROOT to your repository path."
        ) from exc

try:
    from Telemetry.Telemetry import Telemetry
except Exception as exc:
    raise ImportError(
        "Telemetry package was not found. Ensure gcs-packet is installed and importable."
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
        telemetry.speed = snap["speed"]
        telemetry.pitch = snap["pitch"]
        telemetry.yaw = snap["yaw"]
        telemetry.roll = snap["roll"]
        telemetry.altitude = snap["altitude"]
        telemetry.battery_life = self.battery_life_default
        telemetry.current_latitude = snap["latitude"]
        telemetry.current_longitude = snap["longitude"]
        telemetry.vehicle_status = snap["vehicle_status"]
        telemetry.patient_status = self.patient_status_default
        telemetry.message_flag = self.message_flag_default
        telemetry.message_lat = self.message_lat_default
        telemetry.message_lon = self.message_lon_default
        telemetry.last_updated = time.time()

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
