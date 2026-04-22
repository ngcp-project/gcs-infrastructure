import socket
import struct
import rclpy
from rclpy.node import Node
from ugv_msgs.msg import UGVTelemetry

# Binary packet layout (50 bytes, little-endian) — matches xsens_data_conversion.py:
# Bytes  0-1  : reserved          (2 bytes)
# Bytes  2-5  : speed_fps         (float32)
# Bytes  6-9  : pitch_deg         (float32)
# Bytes 10-13 : yaw_deg           (float32)
# Bytes 14-17 : roll_deg          (float32)
# Bytes 18-21 : altitude_ft       (float32)
# Bytes 22-33 : reserved          (12 bytes)
# Bytes 34-41 : latitude          (float64)
# Bytes 42-49 : longitude         (float64)
PACKET_FORMAT = '<xx fffff 12x dd'


class GcsTelemetrySender(Node):
    def __init__(self):
        super().__init__('gcs_telemetry_sender')

        self.declare_parameter('gcs_ip', '192.168.1.100')
        self.declare_parameter('gcs_port', 5005)

        gcs_ip   = self.get_parameter('gcs_ip').value
        gcs_port = int(self.get_parameter('gcs_port').value)

        self._gcs_addr = (gcs_ip, gcs_port)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.create_subscription(UGVTelemetry, '/ngcp/telemetry', self._telemetry_cb, 10)

        self.get_logger().info(f'Telemetry subscriber ready, forwarding UDP to {gcs_ip}:{gcs_port}')

    def _telemetry_cb(self, msg: UGVTelemetry):
        # Log to ROS
        self.get_logger().info(
            f'[Telemetry] '
            f'Speed: {msg.speed_fps:.2f} ft/s | '
            f'Pitch: {msg.pitch_deg:.2f}° | '
            f'Yaw: {msg.yaw_deg:.2f}° | '
            f'Roll: {msg.roll_deg:.2f}° | '
            f'Alt: {msg.altitude_ft:.2f} ft | '
            f'Pos: ({msg.latitude:.6f}, {msg.longitude:.6f})'
        )

        # Forward over UDP
        packet = struct.pack(
            PACKET_FORMAT,
            msg.speed_fps, msg.pitch_deg, msg.yaw_deg, msg.roll_deg, msg.altitude_ft,
            msg.latitude, msg.longitude
        )
        try:
            self._sock.sendto(packet, self._gcs_addr)
        except Exception as ex:
            self.get_logger().warning(f'UDP send failed: {ex}')

    def destroy_node(self):
        self._sock.close()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = GcsTelemetrySender()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
