import math

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node


class TurtleSquare(Node):
    def __init__(self):
        super().__init__('turtle_square')
        self.declare_parameter('cmd_vel_topic', '/turtle1/cmd_vel')
        self.declare_parameter('linear_speed', 2.0)
        self.declare_parameter('angular_speed', math.pi / 2.0)
        self.declare_parameter('phase_duration', 1.0)
        self.declare_parameter('repeat', True)

        cmd_vel_topic = self.get_parameter('cmd_vel_topic').value
        self.linear_speed = float(self.get_parameter('linear_speed').value)
        self.angular_speed = float(self.get_parameter('angular_speed').value)
        self.repeat = bool(self.get_parameter('repeat').value)

        self.publisher_ = self.create_publisher(Twist, cmd_vel_topic, 10)
        self.timer_period = 0.1
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        phase_duration = float(self.get_parameter('phase_duration').value)
        self.ticks_per_phase = max(1, int(phase_duration / self.timer_period))
        self.phase = 0
        self.tick = 0

    def timer_callback(self):
        msg = Twist()

        if self.phase >= 8:
            if self.repeat:
                self.phase = 0
            else:
                self.publisher_.publish(msg)
                self.get_logger().info('Square motion finished.')
                self.timer.cancel()
                return

        if self.phase % 2 == 0:
            msg.linear.x = self.linear_speed
            msg.angular.z = 0.0
        else:
            msg.linear.x = 0.0
            msg.angular.z = self.angular_speed

        self.publisher_.publish(msg)
        self.tick += 1

        if self.tick >= self.ticks_per_phase:
            self.tick = 0
            self.phase += 1


def main(args=None):
    rclpy.init(args=args)
    node = TurtleSquare()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
