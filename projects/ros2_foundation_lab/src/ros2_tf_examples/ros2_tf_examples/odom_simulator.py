import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import TransformBroadcaster
from tf_transformations import quaternion_from_euler


class OdomSimulator(Node):
    def __init__(self):
        super().__init__('odom_simulator')

        self.br = TransformBroadcaster(self)
        self.timer = self.create_timer(0.05, self.timer_callback)  # 20 Hz
        self.radius = 1.0
        self.omega = 0.5
        self.start_time = self.get_clock().now()

    def timer_callback(self):
        now = self.get_clock().now()
        t = (now - self.start_time).nanoseconds / 1e9

        # Circular motion around the odom frame origin.
        x = self.radius * math.cos(self.omega * t)
        y = self.radius * math.sin(self.omega * t)

        # Set yaw to follow the tangent direction.
        roll = 0.0
        pitch = 0.0
        yaw = self.omega * t + math.pi / 2

        qx, qy, qz, qw = quaternion_from_euler(roll, pitch, yaw)

        trans = TransformStamped()
        trans.header.stamp = now.to_msg()
        trans.header.frame_id = 'odom'
        trans.child_frame_id = 'base_link'
        trans.transform.translation.x = x
        trans.transform.translation.y = y
        trans.transform.translation.z = 0.0
        trans.transform.rotation.x = qx
        trans.transform.rotation.y = qy
        trans.transform.rotation.z = qz
        trans.transform.rotation.w = qw

        self.br.sendTransform(trans)


def main(args=None):
    rclpy.init(args=args)
    node = OdomSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
