import struct

import rclpy
from rclpy.node import Node
from ugv_msgs.msg import UGVTelemetry

from xbee import XBee


# 50-byte binary payload format shared with the sender.
PACKET_FORMAT = '<xx fffff 12x dd'
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)


class GcsXbeeListener(Node):
    def __init__(self):
        super().__init__('gcs_xbee_listener')

        self.declare_parameter('xbee_port', 'COM5')
        self.declare_parameter('xbee_baud', 115200)
        self.declare_parameter('publish_topic', '/ngcp/telemetry/xbee_rx')

        self._xbee_port = str(self.get_parameter('xbee_port').value)
        self._xbee_baud = int(self.get_parameter('xbee_baud').value)
        publish_topic = str(self.get_parameter('publish_topic').value)

        self._xbee = XBee(self._xbee_port, self._xbee_baud)
        self._xbee.open()

        self._pub = self.create_publisher(UGVTelemetry, publish_topic, 20)
        self.create_timer(0.01, self._poll_xbee)

        self.get_logger().info(
            f'XBee listener ready on {self._xbee_port}@{self._xbee_baud}, '
            f'publishing decoded telemetry to {publish_topic}'
        )

    def _poll_xbee(self):
        try:
            frame = self._xbee.retrieve_data()
        except Exception as ex:
            self.get_logger().warning(f'XBee receive failed: {ex}')
            return

        if frame is None:
            return

        raw = getattr(frame, 'received_data', None)
        if raw is None:
            raw = getattr(frame, 'data', None)

        if raw is None:
            return

        if len(raw) != PACKET_SIZE:
            self.get_logger().warning(f'Unexpected payload size: {len(raw)} bytes')
            return

        speed, pitch, yaw, roll, alt, lat, lon = struct.unpack(PACKET_FORMAT, raw)

        out = UGVTelemetry()
        out.speed_fps = float(speed)
        out.pitch_deg = float(pitch)
        out.yaw_deg = float(yaw)
        out.roll_deg = float(roll)
        out.altitude_ft = float(alt)
        out.latitude = float(lat)
        out.longitude = float(lon)
        self._pub.publish(out)

    def destroy_node(self):
        try:
            self._xbee.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GcsXbeeListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
