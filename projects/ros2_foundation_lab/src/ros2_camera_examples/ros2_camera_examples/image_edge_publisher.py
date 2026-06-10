import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge


class ImageEdgePublisher(Node):
    def __init__(self):
        super().__init__('image_edge_publisher')
        self.bridge = CvBridge()
        self.current_frame = None

        # Subscribe to the raw camera image.
        self.subscription = self.create_subscription(
            Image, 'image_raw', self.image_callback, 10)

        # Republish the Canny edge image.
        self.edge_publisher = self.create_publisher(Image, 'image_edge', 10)

    def image_callback(self, msg):
        self.current_frame = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="bgr8")

        edge = cv2.Canny(self.current_frame, 50, 300)
        edge_msg = self.bridge.cv2_to_imgmsg(edge, encoding="mono8")
        edge_msg.header.stamp = msg.header.stamp
        edge_msg.header.frame_id = msg.header.frame_id

        self.edge_publisher.publish(edge_msg)
        # self.get_logger().info('Publishing Canny edge image...')


def main(args=None):
    rclpy.init(args=args)
    node = ImageEdgePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
