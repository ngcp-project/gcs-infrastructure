import rclpy
from rclpy.node import Node
from sensor_msgs.msg import NavSatFix
from geometry_msgs import Vector3Stamped

class CoordDumper(Node):
    def __init__(self):
        super().__init__('coord_dumper')
        self.gnss_sub = self.create_subscription(NavSatFix, '/gnss', self.gnss_sub, 10)
        self.euler_sub = self.create_subscription(Vector3Stamped, '/filter/euler', self.euler_sub, 10)
        self.count = 0
        self.latest_z = 0
        open('ntrip_coords.txt', 'w').close()

    def euler_callback(self, msg):
        self.latest_z = msg.vector.z

    def gnss_callback(self, msg):
       # if msg.status.status < 0:
        #    self.get_logger().warn('No fix yet, skipping...')
         #    return
        if self.latest_z is None:
            return
        if self.count < 3:
            with open('ntrip_coords.txt', 'a') as f:
                f.write(f"latitude: {msg.latitude}, longitude: {msg.longitude}, heading: {msg.latest_z}\n")
            self.count += 1
        else:
            rclpy.shutdown()

def main():
    rclpy.init()
    node = CoordDumper()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
