#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class SimpleLidarAvoider(Node):
    def __init__(self):
        super().__init__('simple_lidar_avoider')

        self.declare_parameter('scan_topic', '/lee/scan')
        self.declare_parameter('cmd_vel_topic', '/lee/cmd_vel')
        self.declare_parameter('obstacle_distance', 0.55)
        self.declare_parameter('front_angle_deg', 25.0)
        self.declare_parameter('forward_speed', 0.16)
        self.declare_parameter('turn_speed', 0.45)
        self.declare_parameter('turn_direction', 'right')
        self.declare_parameter('control_rate', 10.0)

        self.scan_topic = self.get_parameter('scan_topic').value
        self.cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.obstacle_distance = self.get_parameter('obstacle_distance').value
        self.front_angle_deg = self.get_parameter('front_angle_deg').value
        self.forward_speed = self.get_parameter('forward_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value
        self.turn_direction = self.get_parameter('turn_direction').value

        if self.turn_direction not in ('left', 'right'):
            self.get_logger().warn(
                f'turn_direction="{self.turn_direction}" is invalid. Falling back to "right".'
            )
            self.turn_direction = 'right'

        self.latest_scan = None
        self.cmd_pub = self.create_publisher(Twist, self.cmd_vel_topic, 10)
        self.scan_sub = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self.scan_callback,
            10,
        )

        control_rate = float(self.get_parameter('control_rate').value)
        if control_rate <= 0.0:
            self.get_logger().warn(
                'control_rate must be positive. Falling back to 10.0 Hz.'
            )
            control_rate = 10.0

        control_period = 1.0 / control_rate
        self.timer = self.create_timer(control_period, self.control_callback)

        self.get_logger().info(
            f'Simple LiDAR avoider: {self.scan_topic} -> {self.cmd_vel_topic}'
        )

    def scan_callback(self, msg):
        self.latest_scan = msg

    def get_front_distance(self, scan):
        half_angle = math.radians(self.front_angle_deg)
        front_ranges = []

        for index, distance in enumerate(scan.ranges):
            if not math.isfinite(distance):
                continue
            if distance < scan.range_min or distance > scan.range_max:
                continue

            angle = scan.angle_min + index * scan.angle_increment
            if -half_angle <= angle <= half_angle:
                front_ranges.append(distance)

        return min(front_ranges) if front_ranges else math.inf

    def control_callback(self):
        if self.latest_scan is None:
            self.publish_stop()
            return

        front_distance = self.get_front_distance(self.latest_scan)
        cmd = Twist()

        if front_distance < self.obstacle_distance:
            cmd.linear.x = 0.0
            cmd.angular.z = self.get_turn_speed()
        else:
            cmd.linear.x = self.forward_speed
            cmd.angular.z = 0.0

        self.cmd_pub.publish(cmd)

    def get_turn_speed(self):
        if self.turn_direction == 'left':
            return self.turn_speed
        return -self.turn_speed

    def publish_stop(self):
        self.cmd_pub.publish(Twist())

    def destroy_node(self):
        self.publish_stop()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = SimpleLidarAvoider()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
