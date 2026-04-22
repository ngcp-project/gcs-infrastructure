import re
import struct

import rclpy
from rclpy.node import Node
from ugv_msgs.msg import UGVTelemetry

from xbee import XBee


# 50-byte binary payload format shared with the UDP telemetry path.
PACKET_FORMAT = '<xx fffff 12x dd'


class GcsXbeeSender(Node):
    def __init__(self):
        super().__init__('gcs_xbee_sender')

        self.declare_parameter('xbee_port', 'COM4')
        self.declare_parameter('xbee_baud', 115200)
        self.declare_parameter('destination_mac', '0013A20000000000')
        self.declare_parameter('telemetry_topic', '/ngcp/telemetry')

        self._xbee_port = str(self.get_parameter('xbee_port').value)
        self._xbee_baud = int(self.get_parameter('xbee_baud').value)
        self._destination_mac = str(self.get_parameter('destination_mac').value).upper()
        telemetry_topic = str(self.get_parameter('telemetry_topic').value)

        if not re.fullmatch(r'[0-9A-F]{16}', self._destination_mac):
            raise ValueError(
                'destination_mac must be exactly 16 hex characters (64-bit MAC), '
                f'got: {self._destination_mac}'
            )

        self._xbee = XBee(self._xbee_port, self._xbee_baud)
        self._xbee.open()

        self.create_subscription(UGVTelemetry, telemetry_topic, self._telemetry_cb, 20)

        self.get_logger().info(
            f'XBee sender ready on {self._xbee_port}@{self._xbee_baud}, '
            f'sending telemetry to {self._destination_mac}'
        )

    def _telemetry_cb(self, msg: UGVTelemetry):
        payload = struct.pack(
            PACKET_FORMAT,
            float(msg.speed_fps),
            float(msg.pitch_deg),
            float(msg.yaw_deg),
            float(msg.roll_deg),
            float(msg.altitude_ft),
            float(msg.latitude),
            float(msg.longitude),
        )

        try:
            self._xbee.transmit_data(payload, address=self._destination_mac)
        except Exception as ex:
            self.get_logger().warning(f'XBee transmit failed: {ex}')

    def destroy_node(self):
        try:
            self._xbee.close()
        except Exception:
            pass
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GcsXbeeSender()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
