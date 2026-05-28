import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge

from rcl_interfaces.msg import SetParametersResult

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.declare_parameter('publish_rate', 15.0)
        self.declare_parameter('topic_name', 'image_raw')
        self.declare_parameter('image_size', [640, 480])
        self.declare_parameter('frame_id', 'camera_link')

        self.rate = self.get_parameter('publish_rate').value
        self.topic = self.get_parameter('topic_name').value
        self.size = self.get_parameter('image_size').value
        self.frame_id = self.get_parameter('frame_id').value

        self.add_on_set_parameters_callback(self.parameter_callback)

        self.publisher_ = self.create_publisher(Image, self.topic, 10)
        self.timer = self.create_timer(1.0 / self.rate, self.timer_callback)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.size[0]))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.size[1]))
        self.bridge = CvBridge()

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'publish_rate':
                self.rate = param.value

                self.timer.cancel()
                self.timer = self.create_timer(1.0 / self.rate, self.timer_callback)

                self.get_logger().info(f'Publish rate updated: {self.rate}Hz')

            elif param.name == 'image_size':
                self.size = param.value
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.size[0]))
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.size[1]))
                self.get_logger().info(f'Image size updated: {self.size}')
            elif param.name == 'frame_id':
                self.frame_id = param.value
        return SetParametersResult(successful=True)

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:

            # Convert the OpenCV frame into a ROS2 Image message and publish it.
            resized = cv2.resize(frame, tuple(self.size))
            img_msg = self.bridge.cv2_to_imgmsg(resized, encoding="bgr8")
            
            img_msg.header.stamp = self.get_clock().now().to_msg()
            img_msg.header.frame_id = self.frame_id

            self.publisher_.publish(img_msg)
            self.get_logger().info('Publishing image frame...')


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
