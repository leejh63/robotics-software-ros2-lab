import math

import rclpy
from geometry_msgs.msg import TransformStamped
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster
from tf_transformations import quaternion_from_euler


class TfTreeSimulator(Node):
    def __init__(self):
        super().__init__('tf_tree_simulator')

        self.declare_parameter('map_frame', 'map')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_link')
        self.declare_parameter('left_frame', 'left_marker')
        self.declare_parameter('right_frame', 'right_marker')
        self.declare_parameter('radius', 1.0)
        self.declare_parameter('omega', 0.5)

        self.map_frame = self.get_parameter(
            'map_frame').get_parameter_value().string_value
        self.odom_frame = self.get_parameter(
            'odom_frame').get_parameter_value().string_value
        self.base_frame = self.get_parameter(
            'base_frame').get_parameter_value().string_value
        self.left_frame = self.get_parameter(
            'left_frame').get_parameter_value().string_value
        self.right_frame = self.get_parameter(
            'right_frame').get_parameter_value().string_value
        self.radius = self.get_parameter(
            'radius').get_parameter_value().double_value
        self.omega = self.get_parameter(
            'omega').get_parameter_value().double_value

        self.static_br = StaticTransformBroadcaster(self)
        self.br = TransformBroadcaster(self)
        self.start_time = self.get_clock().now()

        self.publish_static_map_to_odom()
        self.timer = self.create_timer(0.05, self.timer_callback)

    def publish_static_map_to_odom(self):
        trans = TransformStamped()
        trans.header.stamp = self.get_clock().now().to_msg()
        trans.header.frame_id = self.map_frame
        trans.child_frame_id = self.odom_frame
        trans.transform.translation.x = 0.0
        trans.transform.translation.y = 0.0
        trans.transform.translation.z = 0.0
        trans.transform.rotation.w = 1.0

        self.static_br.sendTransform(trans)

    def timer_callback(self):
        now = self.get_clock().now()
        t = (now - self.start_time).nanoseconds / 1e9

        transforms = [
            self.make_odom_to_base(now, t),
            self.make_base_to_left(now, t),
            self.make_base_to_right(now, t),
        ]
        self.br.sendTransform(transforms)

    def make_odom_to_base(self, now, t):
        x = self.radius * math.cos(self.omega * t)
        y = self.radius * math.sin(self.omega * t)
        yaw = self.omega * t + math.pi / 2

        return self.make_transform(
            now,
            self.odom_frame,
            self.base_frame,
            x,
            y,
            0.0,
            0.0,
            0.0,
            yaw)

    def make_base_to_left(self, now, t):
        x = 0.65 + 0.12 * math.sin(1.5 * t)
        y = 0.45
        yaw = 0.4 * math.sin(2.0 * t)

        return self.make_transform(
            now,
            self.base_frame,
            self.left_frame,
            x,
            y,
            0.0,
            0.0,
            0.0,
            yaw)

    def make_base_to_right(self, now, t):
        x = 0.65 + 0.12 * math.cos(1.5 * t)
        y = -0.45
        yaw = -0.4 * math.sin(2.0 * t)

        return self.make_transform(
            now,
            self.base_frame,
            self.right_frame,
            x,
            y,
            0.0,
            0.0,
            0.0,
            yaw)

    def make_transform(
            self, now, parent, child, x, y, z, roll, pitch, yaw):
        qx, qy, qz, qw = quaternion_from_euler(roll, pitch, yaw)

        trans = TransformStamped()
        trans.header.stamp = now.to_msg()
        trans.header.frame_id = parent
        trans.child_frame_id = child
        trans.transform.translation.x = x
        trans.transform.translation.y = y
        trans.transform.translation.z = z
        trans.transform.rotation.x = qx
        trans.transform.rotation.y = qy
        trans.transform.rotation.z = qz
        trans.transform.rotation.w = qw

        return trans


def main(args=None):
    rclpy.init(args=args)
    node = TfTreeSimulator()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
