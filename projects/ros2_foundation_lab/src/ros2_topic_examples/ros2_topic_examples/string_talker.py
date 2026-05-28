import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StringTalker(Node):
    def __init__(self):
        super().__init__('string_talker')
        self.declare_parameter('topic_name', 'chatter')
        self.declare_parameter('publish_period', 0.5)

        topic_name = self.get_parameter('topic_name').value
        publish_period = float(self.get_parameter('publish_period').value)

        self.publisher_ = self.create_publisher(String, topic_name, 10)
        self.timer = self.create_timer(publish_period, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'hello ros2 foundation [{self.count}]'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')
        self.count += 1


def main(args=None):
    rclpy.init(args=args)
    node = StringTalker()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
