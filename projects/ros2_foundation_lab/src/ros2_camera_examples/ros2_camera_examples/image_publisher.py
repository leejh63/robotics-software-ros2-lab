import rclpy
from rcl_interfaces.msg import SetParametersResult
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge


class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.declare_parameter('publish_rate', 15.0)
        self.declare_parameter('topic_name', 'image_raw')
        self.declare_parameter('image_size', [640, 480])
        self.declare_parameter('frame_id', 'camera_link')
        self.declare_parameter('camera_index', 0)

        self.rate = self._validate_publish_rate(
            self.get_parameter('publish_rate').value)
        self.topic = self.get_parameter('topic_name').value
        self.size = self._validate_image_size(
            self.get_parameter('image_size').value)
        self.frame_id = self.get_parameter('frame_id').value
        self.camera_index = int(self.get_parameter('camera_index').value)

        self.add_on_set_parameters_callback(self.parameter_callback)

        self.publisher_ = self.create_publisher(Image, self.topic, 10)
        self.timer = self.create_timer(1.0 / self.rate, self.timer_callback)
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f'Failed to open camera index {self.camera_index}')
        self._apply_camera_size()
        self.bridge = CvBridge()

    @staticmethod
    def _validate_publish_rate(value):
        rate = float(value)
        if rate <= 0.0:
            raise ValueError('publish_rate must be greater than 0.')
        return rate

    @staticmethod
    def _validate_image_size(value):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError('image_size must be a two-item list: [width, height].')

        width, height = int(value[0]), int(value[1])
        if width <= 0 or height <= 0:
            raise ValueError('image_size width and height must be greater than 0.')
        return [width, height]

    def _apply_camera_size(self):
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, int(self.size[0]))
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(self.size[1]))

    def parameter_callback(self, params):
        try:
            for param in params:
                if param.name == 'publish_rate':
                    self.rate = self._validate_publish_rate(param.value)

                    self.timer.cancel()
                    self.timer = self.create_timer(
                        1.0 / self.rate, self.timer_callback)

                    self.get_logger().info(f'Publish rate updated: {self.rate}Hz')

                elif param.name == 'image_size':
                    self.size = self._validate_image_size(param.value)
                    self._apply_camera_size()
                    self.get_logger().info(f'Image size updated: {self.size}')

                elif param.name == 'frame_id':
                    self.frame_id = str(param.value)

            return SetParametersResult(successful=True)
        except (TypeError, ValueError) as exc:
            return SetParametersResult(successful=False, reason=str(exc))

    def destroy_node(self):
        if hasattr(self, 'cap') and self.cap is not None:
            self.cap.release()
        super().destroy_node()

    def timer_callback(self):
        ret, frame = self.cap.read()
        if ret:
            # Convert the OpenCV frame into a ROS2 Image message and publish it.
            resized = cv2.resize(frame, tuple(self.size))
            img_msg = self.bridge.cv2_to_imgmsg(resized, encoding='bgr8')

            img_msg.header.stamp = self.get_clock().now().to_msg()
            img_msg.header.frame_id = self.frame_id

            self.publisher_.publish(img_msg)
            self.get_logger().debug('Published image frame.')


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ImagePublisher()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
