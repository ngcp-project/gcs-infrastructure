from setuptools import setup

package_name = 'ugv_telemetry'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/ugv_telemetry.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ugv',
    maintainer_email='todo@todo.com',
    description='Xsens telemetry conversion node for UGV GCS',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'xsens_data_conversion = ugv_telemetry.xsens_data_conversion:main',
            'gcs_telemetry_sender = ugv_telemetry.gcs_telemetry_sender:main',
            'gcs_udp_listener = ugv_telemetry.gcs_udp_listener:main',
            'gcs_xbee_sender = ugv_telemetry.gcs_xbee_sender:main',
            'gcs_xbee_listener = ugv_telemetry.gcs_xbee_listener:main',
        ],
    },
)
