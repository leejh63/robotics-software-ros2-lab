import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class StringListener(Node):
    def __init__(self):
        super().__init__('string_listener')
        self.declare_parameter('topic_name', 'chatter')

        topic_name = self.get_parameter('topic_name').value
        self.subscription = self.create_subscription(
            String,
            topic_name,
            self.listener_callback,
            10,
        )

    def listener_callback(self, msg):
        self.get_logger().info(f'Received: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)
    node = StringListener()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
