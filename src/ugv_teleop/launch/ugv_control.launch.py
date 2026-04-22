from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='joy',
            executable='joy_node',
            name='joy_node',
            output='screen',
            parameters=[{'dev': '/dev/input/js0'}]
        ),
        Node(
            package='ugv_teleop',
            executable='ugv_control_pub',
            name='ugv_control_pub',
            output='screen',
            parameters=[{
                'arm0_lower_limit': 0.0,
                'arm0_upper_limit': 170.0,
                'arm1_lower_limit': 75.0,
                'arm1_upper_limit': 225.0,
                'inc_dec_val': 5.0,
            }]
        ),
        Node(
            package='ugv_teleop',
            executable='ugv_control_sub',
            name='ugv_control_sub',
            output='screen',
            parameters=[{
                'client_ip': '169.254.155.100',
                'client_port': 8,
                'heartbeat_timeout': 3.0,
            }]
        ),
    ])
