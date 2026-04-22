#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from ugv_msgs.msg import ManCtrl, AutoCtrl
from sensor_msgs.msg import Joy
from rclpy.qos import qos_profile_system_default, qos_profile_sensor_data
from ugv_teleop.ugv_arm import ArmController

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

class UgvControlNode(Node):
    def __init__(self):
        super().__init__('ugv_control_pub')

        self.declare_parameter('max_joy_val', float(2**15))
        self.declare_parameter('dead_zone', 0.15)
        self.declare_parameter('upper_steer_limit', 1.0)
        self.declare_parameter('inc_dec_val', 5.0)
        self.declare_parameter('arm0_lower_limit', 0.0)
        self.declare_parameter('arm0_upper_limit', 170.0)
        self.declare_parameter('arm1_lower_limit', 75.0)
        self.declare_parameter('arm1_upper_limit', 225.0)
        self.declare_parameter('watchdog_timeout', 0.25)

        self.max_joy_val       = self.get_parameter('max_joy_val').value
        self.dead_zone         = self.get_parameter('dead_zone').value
        self.upper_steer_limit = self.get_parameter('upper_steer_limit').value
        self.inc_dec_val       = self.get_parameter('inc_dec_val').value
        self.arm0_lo           = self.get_parameter('arm0_lower_limit').value
        self.arm0_hi           = self.get_parameter('arm0_upper_limit').value
        self.arm1_lo           = self.get_parameter('arm1_lower_limit').value
        self.arm1_hi           = self.get_parameter('arm1_upper_limit').value

        self.last_joy_time = time.monotonic()
        self._last_timer_time = time.monotonic()

        self.man_pub = self.create_publisher(ManCtrl, 'man_ctrl', qos_profile_system_default)
        self.auto_pub = self.create_publisher(AutoCtrl, 'auto_ctrl', qos_profile_system_default)
        self.create_subscription(Joy, 'joy', self.on_joy, qos_profile_sensor_data)

        self.man_obj = ManCtrl()
        self.auto_obj = AutoCtrl()
        self.man_obj.arm_cmd = [0.0, self.arm1_lo]
        self.man_obj.linear_vel = 0.0
        self.man_obj.steer_cmd = 0.0
        self.man_obj.auto_en = False
        self.auto_obj.auto_en = False

        self.cmd_vel = 0.0
        self.cmd_steer = 0.0
        self.l_bumper = 0
        self.r_bumper = 0
        self.ud_dpad = 0
        self.lr_dpad = 0
        self.a_btn = 0
        self.b_btn = 0
        self.x_btn = 0
        self.y_btn = 0
        self.lt_val = 0
        self.rt_val = 0

        self.arm_controller = ArmController(
            num_joints=2,
            inc_dec_val=float(self.inc_dec_val),
            joint0_limits=(self.arm0_lo, self.arm0_hi),
            joint1_limits=(self.arm1_lo, self.arm1_hi),
        )

        self.timer = self.create_timer(0.02, self.timer_callback)  # 50 Hz
        self.get_logger().info('UGV CONTROL PUBLISHER STARTED AT 50 HZ')

    def timer_callback(self):
        now = time.monotonic()
        dt = now - self._last_timer_time
        self._last_timer_time = now
        dt = max(0.0, min(dt, 0.1))

        self.man_obj.linear_vel = self.cmd_vel
        self.man_obj.steer_cmd = clamp(
            self.cmd_steer,
            -self.upper_steer_limit, self.upper_steer_limit
        )

        # LT held = arm control mode (D-pad controls 2 joints)
        LT_ON = self.lt_val > 1000
        if LT_ON:
            self.arm_controller.process_arm_control(
                dt=dt,
                ud_pad=self.ud_dpad,
                lr_pad=self.lr_dpad,
            )

        positions = self.arm_controller.get_positions()
        self.man_obj.arm_cmd = positions

        self.get_logger().info(
            f'PUB MAN vel={self.man_obj.linear_vel:.3f}, '
            f'steer={self.man_obj.steer_cmd:.3f}, '
            f'arm=[{positions[0]:.3f},{positions[1]:.3f}]'
        )
        self.man_pub.publish(self.man_obj)

    def on_joy(self, msg: Joy):
        self.last_joy_time = time.monotonic()

        if len(msg.axes) < 8 or len(msg.buttons) < 6:
            self.get_logger().warn(
                f"Joy message too small: axes={len(msg.axes)} buttons={len(msg.buttons)}"
            )
            return

        self.cmd_vel   = -msg.axes[1]
        self.cmd_steer = -msg.axes[3]

        self.lt_val = int((1 - msg.axes[2]) * self.max_joy_val / 2)
        self.rt_val = int((1 - msg.axes[5]) * self.max_joy_val / 2)
        self.l_bumper  = int(msg.buttons[4])
        self.r_bumper  = int(msg.buttons[5])
        self.a_btn     = int(msg.buttons[0])
        self.b_btn     = int(msg.buttons[1])
        self.x_btn     = int(msg.buttons[2])
        self.y_btn     = int(msg.buttons[3])
        self.lr_dpad   = int(msg.axes[6])
        self.ud_dpad   = int(msg.axes[7])

        self.get_logger().debug(
            f'vel={self.cmd_vel:.2f} steer={self.cmd_steer:.2f} '
            f'lt={self.lt_val} rt={self.rt_val} '
            f'dpad=({self.lr_dpad},{self.ud_dpad})'
        )

    def destroy_node(self):
        self.get_logger().info('Shutting down ugv_control_pub...')
        super().destroy_node()

def main():
    rclpy.init()
    node = UgvControlNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
