import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from std_srvs.srv import Trigger
import cv2
from cv_bridge import CvBridge


class ImageProcessor(Node):
    def __init__(self):
        super().__init__('image_processor')
        self.bridge = CvBridge()
        self.raw_frame = None
        self.yolo_frame = None
        self.edge_frame = None

        self.declare_parameter('snapshot_target', 'raw')

        self.raw_subscription = self.create_subscription(
            Image, 'image_raw', self.raw_image_callback, 10)
        self.yolo_subscription = self.create_subscription(
            Image, 'image_yolo', self.yolo_image_callback, 10)
        self.edge_subscription = self.create_subscription(
            Image, 'image_edge', self.edge_image_callback, 10)

        self.srv = self.create_service(
            Trigger, 'capture_snapshot', self.capture_callback)

    def raw_image_callback(self, msg):
        # Convert the ROS2 Image message into an OpenCV image.
        self.raw_frame = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="bgr8")

        cv2.imshow("Camera View", self.raw_frame)
        cv2.waitKey(1)  # Required for GUI window refresh.

    def yolo_image_callback(self, msg):
        self.yolo_frame = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="bgr8")

        cv2.imshow("YOLO View", self.yolo_frame)
        cv2.waitKey(1)

    def edge_image_callback(self, msg):
        self.edge_frame = self.bridge.imgmsg_to_cv2(
            msg, desired_encoding="mono8")

        cv2.imshow("Canny View", self.edge_frame)
        cv2.waitKey(1)

    def capture_callback(self, request, response):
        target = self.get_parameter('snapshot_target').value

        snapshot_map = {
            'raw': (self.raw_frame, 'snapshot_raw.jpg'),
            'yolo': (self.yolo_frame, 'snapshot_yolo.jpg'),
            'canny': (self.edge_frame, 'snapshot_canny.jpg'),
        }

        if target not in snapshot_map:
            response.success = False
            response.message = "snapshot_target must be one of: raw, yolo, canny."
            return response

        frame, filename = snapshot_map[target]
        if frame is None:
            response.success = False
            response.message = f"{target} image has not been received yet."
            return response

        cv2.imwrite(filename, frame)
        response.success = True
        response.message = f"{target} snapshot saved: {filename}"
        return response


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = ImageProcessor()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        if node is not None:
            node.destroy_node()
        cv2.destroyAllWindows()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
