from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from pathlib import Path


def generate_launch_description():
    ntrip_params = Path(get_package_share_directory('ntrip'), 'config', 'ntrip-param.yaml')
    xsens_params = Path(get_package_share_directory('xsens_mti_ros2_driver'), 'param', 'xsens_mti_node.yaml')

    return LaunchDescription([
        Node(
            package='xsens_mti_ros2_driver',
            executable='xsens_mti_node',
            name='xsens_mti_node',
            output='screen',
            parameters=[str(xsens_params)]
        ),
        Node(
            package='ntrip',
            executable='ntrip',
            name='ntrip_client',
            output='screen',
            parameters=[str(ntrip_params)]
        ),
        Node(
            package='ugv_telemetry',
            executable='xsens_data_conversion',
            name='xsens_data_conversion',
            output='screen'
        ),
        Node(
            package='ugv_telemetry',
            executable='gcs_telemetry_sender',
            name='gcs_telemetry_sender',
            output='screen',
            parameters=[{
                'gcs_ip': '192.168.1.100',
                'gcs_port': 5005,
            }]
        ),
    ])
