import sys
from pathlib import Path

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import cv2
from cv_bridge import CvBridge


def add_local_venv_site_packages():
    python_version = f'python{sys.version_info.major}.{sys.version_info.minor}'

    for parent in Path(__file__).resolve().parents:
        site_packages = parent / '.venv' / 'lib' / python_version / 'site-packages'
        if site_packages.exists():
            sys.path.insert(0, str(site_packages))
            return


add_local_venv_site_packages()

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class YoloImagePublisher(Node):
    def __init__(self):
        super().__init__('yolo_image_publisher')
        self.bridge = CvBridge()

        self.declare_parameter('model_path', 'yolov8n.pt')
        self.declare_parameter('confidence', 0.5)

        self.model_path = self.get_parameter(
            'model_path').get_parameter_value().string_value
        self.confidence = self.get_parameter(
            'confidence').get_parameter_value().double_value

        if YOLO is None:
            raise ImportError(
                "ultralytics is not installed. "
                "Activate your virtual environment or run 'pip install ultralytics' before retrying.")

        self.get_logger().info(f'Loading YOLO model: {self.model_path}')
        self.model = YOLO(self.model_path)
        self.get_logger().info('YOLO model loaded.')

        # Subscribe to the raw camera image.
        self.subscription = self.create_subscription(
            Image, 'image_raw', self.image_callback, 10)

        # Republish the image annotated by YOLO.
        self.publisher_ = self.create_publisher(Image, 'image_yolo', 10)

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = self.model(frame, conf=self.confidence, verbose=False)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names.get(class_id, str(class_id))
                label = f'{class_name} {confidence:.2f}'

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    label,
                    (x1, max(20, y1 - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2)

        img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        img_msg.header.stamp = msg.header.stamp
        img_msg.header.frame_id = msg.header.frame_id

        self.publisher_.publish(img_msg)
        # self.get_logger().info(f'Publishing YOLO image with {len(result.boxes)} detections.')


def main(args=None):
    rclpy.init(args=args)
    node = YoloImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()
