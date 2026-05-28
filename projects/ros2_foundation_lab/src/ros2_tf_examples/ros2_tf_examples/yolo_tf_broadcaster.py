import rclpy
import tf2_ros
from geometry_msgs.msg import TransformStamped
from ros2_foundation_interfaces.msg import ObjectDetectionArray
from rclpy.node import Node


class TfYoloBroadcaster(Node):
    def __init__(self):
        super().__init__('tf_yolo_broadcaster')

        self.declare_parameter('detection_topic', 'yolo_detections')
        self.declare_parameter('class_filter', 'person')
        self.declare_parameter('parent_frame', '')
        self.declare_parameter('fallback_parent_frame', 'camera_link')
        self.declare_parameter('frame_name_tag', 'example')
        self.declare_parameter('image_width', 320.0)
        self.declare_parameter('image_height', 240.0)
        self.declare_parameter('fixed_depth', 1.0)
        self.declare_parameter('publish_all', False)

        self.detection_topic = self.get_parameter(
            'detection_topic').get_parameter_value().string_value
        self.class_filter = self.get_parameter(
            'class_filter').get_parameter_value().string_value
        self.parent_frame = self.get_parameter(
            'parent_frame').get_parameter_value().string_value
        self.fallback_parent_frame = self.get_parameter(
            'fallback_parent_frame').get_parameter_value().string_value
        self.frame_name_tag = self.get_parameter(
            'frame_name_tag').get_parameter_value().string_value
        self.image_width = self.get_parameter(
            'image_width').get_parameter_value().double_value
        self.image_height = self.get_parameter(
            'image_height').get_parameter_value().double_value
        self.fixed_depth = self.get_parameter(
            'fixed_depth').get_parameter_value().double_value
        self.publish_all = self.get_parameter(
            'publish_all').get_parameter_value().bool_value

        self.br = tf2_ros.TransformBroadcaster(self)
        self.create_subscription(
            ObjectDetectionArray,
            self.detection_topic,
            self.callback,
            10)

        self.get_logger().info(
            f'YOLO TF broadcaster started: topic=/{self.detection_topic}, '
            f'class_filter={self.class_filter}, '
            f'frame_name_tag={self.frame_name_tag}')

    def callback(self, msg):
        parent_frame = self.get_parent_frame(msg)
        published_count = 0

        for index, detection in enumerate(msg.detections):
            if self.class_filter and detection.class_name != self.class_filter:
                continue

            trans = self.detection_to_transform(
                msg,
                detection,
                parent_frame,
                published_count)
            self.br.sendTransform(trans)
            published_count += 1

            self.get_logger().info(
                f'Published TF: {trans.header.frame_id} -> '
                f'{trans.child_frame_id}, '
                f'x={trans.transform.translation.x:.2f}, '
                f'y={trans.transform.translation.y:.2f}, '
                f'z={trans.transform.translation.z:.2f}')

            if not self.publish_all:
                break

    def get_parent_frame(self, msg):
        if self.parent_frame:
            return self.parent_frame
        if msg.header.frame_id:
            return msg.header.frame_id
        return self.fallback_parent_frame

    def detection_to_transform(
            self, msg, detection, parent_frame, published_index):
        center_x, center_y = self.get_bbox_center(detection.bbox)

        normalized_x = (center_x - self.image_width / 2.0) / self.image_width
        normalized_y = (center_y - self.image_height / 2.0) / self.image_height
        depth = self.fixed_depth

        trans = TransformStamped()
        trans.header.stamp = msg.header.stamp
        trans.header.frame_id = parent_frame
        trans.child_frame_id = self.make_child_frame_id(
            detection.class_name, published_index)

        # Camera optical-style mapping: forward=x, left/right=y, up/down=z.
        trans.transform.translation.x = depth
        trans.transform.translation.y = -normalized_x
        trans.transform.translation.z = -normalized_y
        trans.transform.rotation.w = 1.0

        return trans

    def make_child_frame_id(self, class_name, published_index):
        class_part = self.sanitize_frame_part(class_name)
        tag_part = self.sanitize_frame_part(self.frame_name_tag)

        if tag_part:
            return f'object_{class_part}_{tag_part}_{published_index}'

        return f'object_{class_part}_{published_index}'

    def sanitize_frame_part(self, value):
        cleaned = str(value).strip().replace(' ', '_')
        return ''.join(
            char if char.isalnum() or char == '_' else '_'
            for char in cleaned)

    def get_bbox_center(self, bbox):
        if len(bbox) != 4:
            return self.image_width / 2.0, self.image_height / 2.0

        x_min, y_min, x_max, y_max = bbox
        center_x = (float(x_min) + float(x_max)) / 2.0
        center_y = (float(y_min) + float(y_max)) / 2.0

        return center_x, center_y


def main(args=None):
    rclpy.init(args=args)
    node = TfYoloBroadcaster()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
