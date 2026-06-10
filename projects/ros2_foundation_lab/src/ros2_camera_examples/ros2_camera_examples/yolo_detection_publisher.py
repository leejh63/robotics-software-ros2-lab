import sys
from pathlib import Path

import rclpy
from rclpy.node import Node

from ros2_foundation_interfaces.msg import ObjectDetection, ObjectDetectionArray

from sensor_msgs.msg import Image
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


class YoloDetectionPublisher(Node):
    def __init__(self):
        super().__init__('yolo_detection_publisher')
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

        # Publish YOLO detection results as custom messages.
        self.publisher_ = self.create_publisher(
            ObjectDetectionArray, 'yolo_detections', 10)

    def image_callback(self, msg):
        # Convert the ROS Image message into an OpenCV image.
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # Create the detection array message.
        detection_array_msg = ObjectDetectionArray()
        detection_array_msg.header = msg.header

        results = self.model(frame, conf=self.confidence, verbose=False)
        for result in results:
            for box in result.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = result.names.get(class_id, str(class_id))

                # Convert one bounding box into an ObjectDetection message.
                detection_msg = ObjectDetection()
                detection_msg.class_name = class_name
                detection_msg.confidence = confidence
                detection_msg.bbox = [int(x1), int(y1), int(x2), int(y2)]
                detection_array_msg.detections.append(detection_msg)

        self.publisher_.publish(detection_array_msg)
        self.get_logger().info(
            f'Published YOLO detections: {len(detection_array_msg.detections)}')


def main(args=None):
    rclpy.init(args=args)
    node = YoloDetectionPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

