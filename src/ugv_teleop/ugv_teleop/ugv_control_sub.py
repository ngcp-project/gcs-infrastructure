#!/usr/bin/env python3
import socket
import threading
import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile

from ugv_msgs.msg import ManCtrl, AutoCtrl


class UgvControlSubNode(Node):
    def __init__(self):
        super().__init__('ugv_control_sub')

        self.declare_parameter('server_ip', '0.0.0.0')
        self.declare_parameter('server_port', 12345)
        self.declare_parameter('client_ip', '169.254.155.100')
        self.declare_parameter('client_port', 8)
        self.declare_parameter('auto_vel', -1.0)
        self.declare_parameter('auto_steer', 0.0)
        self.declare_parameter('heartbeat_timeout', 3.0)  # seconds before declaring STM32 unreachable

        server_ip        = self.get_parameter('server_ip').value
        server_port      = int(self.get_parameter('server_port').value)
        self.client_ip   = self.get_parameter('client_ip').value
        self.client_port = int(self.get_parameter('client_port').value)
        self.auto_vel    = float(self.get_parameter('auto_vel').value)
        self.auto_steer  = float(self.get_parameter('auto_steer').value)
        self.heartbeat_timeout = float(self.get_parameter('heartbeat_timeout').value)

        # --- UDP socket setup ---
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind((server_ip, server_port))
            self.get_logger().info(
                f'UDP bound to {server_ip}:{server_port}, sending to {self.client_ip}:{self.client_port}'
            )
        except Exception as ex:
            self.get_logger().error(f'UDP bind failed: {ex}')
            raise

        # --- Heartbeat state ---
        self.last_heartbeat = 0.0  # no heartbeat received yet
        self.stm32_alive = False
        self._hb_lock = threading.Lock()

        # Start background thread listening for heartbeat packets from STM32
        self._hb_thread = threading.Thread(target=self._heartbeat_listener, daemon=True)
        self._hb_thread.start()

        # Periodic timer to check heartbeat staleness (1 Hz)
        self.create_timer(1.0, self._check_heartbeat)

        # --- Subscriptions ---
        qos = QoSProfile(depth=10)
        self.man_sub = self.create_subscription(ManCtrl, 'man_ctrl', self.on_man_ctrl, qos)
        self.auto_sub = self.create_subscription(AutoCtrl, 'auto_ctrl', self.on_auto_ctrl, qos)

        self.get_logger().info('UGV CONTROL SUBSCRIBER STARTED')

    # ------------------------------------------------------------------ #
    #  Heartbeat: listen for any UDP packet from the STM32               #
    # ------------------------------------------------------------------ #
    def _heartbeat_listener(self):
        """Background thread: any UDP packet received on our bound socket counts as a heartbeat."""
        while rclpy.ok():
            try:
                self.sock.settimeout(1.0)
                data, addr = self.sock.recvfrom(256)
                with self._hb_lock:
                    self.last_heartbeat = time.monotonic()
                    if not self.stm32_alive:
                        self.stm32_alive = True
                        self.get_logger().info(f'STM32 heartbeat received from {addr}')
            except socket.timeout:
                continue
            except OSError:
                break  # socket closed during shutdown

    def _check_heartbeat(self):
        """Timer callback (1 Hz): warn if no heartbeat within timeout window."""
        with self._hb_lock:
            if self.last_heartbeat == 0.0:
                self.get_logger().warn('No heartbeat from STM32 yet — device may be offline')
                return
            elapsed = time.monotonic() - self.last_heartbeat
            if elapsed > self.heartbeat_timeout:
                if self.stm32_alive:
                    self.stm32_alive = False
                    self.get_logger().error(
                        f'STM32 heartbeat lost! Last seen {elapsed:.1f}s ago'
                    )
            else:
                if not self.stm32_alive:
                    self.stm32_alive = True
                    self.get_logger().info('STM32 heartbeat recovered')

    # ------------------------------------------------------------------ #
    #  Manual control callback                                           #
    # ------------------------------------------------------------------ #
    def on_man_ctrl(self, msg: ManCtrl):
        if getattr(msg, 'auto_en', False):
            self.get_logger().debug('Manual suppressed (auto_en=True).')
            return

        # vel   = round(float(msg.linear_vel), 3)
        # steer = round(float(msg.steer_cmd), 3)
        arm0  = round(float(msg.arm_cmd[0]), 3)
        arm1  = round(float(msg.arm_cmd[1]), 3)

        # add prefix later?
        payload = f'{arm0},{arm1}'.encode()
        self._send(payload, 'MAN')

    # ------------------------------------------------------------------ #
    #  Autonomous control callback                                       #
    # ------------------------------------------------------------------ #
    def on_auto_ctrl(self, msg: AutoCtrl):
        heading_error = float(getattr(msg, 'heading_error', 0.0))
        if abs(heading_error) < 1e-6:
            return

        payload = f'{self.auto_vel:.3f},{self.auto_steer:.3f},{heading_error:.3f}'.encode()
        self._send(payload, 'AUTO')

    # ------------------------------------------------------------------ #
    #  UDP send helper                                                   #
    # ------------------------------------------------------------------ #
    def _send(self, payload: bytes, label: str):
        try:
            self.sock.sendto(payload, (self.client_ip, int(self.client_port)))
            self.get_logger().info(f'Sent {label}: {payload.decode()}')
        except Exception as ex:
            self.get_logger().warning(f'UDP send ({label}) failed: {ex}')

    # ------------------------------------------------------------------ #
    #  Shutdown                                                          #
    # ------------------------------------------------------------------ #
    def destroy_node(self):
        self.get_logger().info('Shutting down UDP subscriber node...')
        try:
            if hasattr(self, 'sock'):
                self.sock.close()
        finally:
            super().destroy_node()


def main():
    rclpy.init()
    node = UgvControlSubNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
