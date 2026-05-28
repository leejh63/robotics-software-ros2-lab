import rclpy
import tf2_ros
from rclpy.node import Node


class TfListener(Node):
    def __init__(self):
        super().__init__('tf_listener')

        self.declare_parameter('target_frame', 'base_link')
        self.declare_parameter('source_frame', 'camera_linright_marker')

        self.target_frame = self.get_parameter(
            'target_frame').get_parameter_value().string_value
        self.source_frame = self.get_parameter(
            'source_frame').get_parameter_value().string_value

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.timer = self.create_timer(1.0, self.timer_callback)

    def timer_callback(self):
        try:
            trans = self.tf_buffer.lookup_transform(
                self.target_frame,
                self.source_frame,
                rclpy.time.Time())

            t = trans.transform.translation
            r = trans.transform.rotation

            self.get_logger().info(
                f'{self.source_frame} in {self.target_frame}: '
                f'x={t.x:.3f}, y={t.y:.3f}, z={t.z:.3f}, '
                f'qx={r.x:.3f}, qy={r.y:.3f}, qz={r.z:.3f}, qw={r.w:.3f}')

        except tf2_ros.LookupException as e:
            self.get_logger().warn(f'TF lookup failed: {e}')
        except tf2_ros.ConnectivityException as e:
            self.get_logger().warn(f'TF connectivity error: {e}')
        except tf2_ros.ExtrapolationException as e:
            self.get_logger().warn(f'TF extrapolation error: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = TfListener()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
