#!/usr/bin/env python3
"""
TurtleBot3 tilted 2D LiDAR point cloud mapper.

The node converts each LaserScan ray into a 3D vector, rotates the vector by
an IMU-derived tilt rotation, and publishes the result as PointCloud2.

This is a compact experiment for visualizing tilted 2D LiDAR data. It does not
perform odometry integration, scan matching, loop closure, or full 3D SLAM.
"""

import math
from collections import deque
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, HistoryPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import Imu, LaserScan, PointCloud2
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header
from tf2_msgs.msg import TFMessage

Vec3 = Tuple[float, float, float]
Mat3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]
Quat = Tuple[float, float, float, float]  # x, y, z, w
TfKey = Tuple[str, str]  # parent_frame, child_frame


def normalize_quat(q: Quat) -> Quat:
    x, y, z, w = q
    n = math.sqrt(x * x + y * y + z * z + w * w)
    if n < 1e-12:
        return (0.0, 0.0, 0.0, 1.0)
    return (x / n, y / n, z / n, w / n)


def quat_conjugate(q: Quat) -> Quat:
    x, y, z, w = q
    return (-x, -y, -z, w)


def quat_multiply(a: Quat, b: Quat) -> Quat:
    ax, ay, az, aw = a
    bx, by, bz, bw = b
    return normalize_quat((
        aw * bx + ax * bw + ay * bz - az * by,
        aw * by - ax * bz + ay * bw + az * bx,
        aw * bz + ax * by - ay * bx + az * bw,
        aw * bw - ax * bx - ay * by - az * bz,
    ))


def quat_to_matrix(q: Quat) -> Mat3:
    x, y, z, w = normalize_quat(q)
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z
    return (
        (1.0 - 2.0 * (yy + zz), 2.0 * (xy - wz), 2.0 * (xz + wy)),
        (2.0 * (xy + wz), 1.0 - 2.0 * (xx + zz), 2.0 * (yz - wx)),
        (2.0 * (xz - wy), 2.0 * (yz + wx), 1.0 - 2.0 * (xx + yy)),
    )


def mat_transpose(m: Mat3) -> Mat3:
    return (
        (m[0][0], m[1][0], m[2][0]),
        (m[0][1], m[1][1], m[2][1]),
        (m[0][2], m[1][2], m[2][2]),
    )


def mat_vec_mul(m: Mat3, v: Vec3) -> Vec3:
    x, y, z = v
    return (
        m[0][0] * x + m[0][1] * y + m[0][2] * z,
        m[1][0] * x + m[1][1] * y + m[1][2] * z,
        m[2][0] * x + m[2][1] * y + m[2][2] * z,
    )


def add_vec(a: Vec3, b: Vec3) -> Vec3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def neg_vec(v: Vec3) -> Vec3:
    return (-v[0], -v[1], -v[2])


def euler_from_quat(q: Quat) -> Tuple[float, float, float]:
    x, y, z, w = normalize_quat(q)

    sinr_cosp = 2.0 * (w * x + y * z)
    cosr_cosp = 1.0 - 2.0 * (x * x + y * y)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    sinp = 2.0 * (w * y - z * x)
    if abs(sinp) >= 1.0:
        pitch = math.copysign(math.pi / 2.0, sinp)
    else:
        pitch = math.asin(sinp)

    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    yaw = math.atan2(siny_cosp, cosy_cosp)
    return roll, pitch, yaw


def quat_from_euler(roll: float, pitch: float, yaw: float) -> Quat:
    cr, sr = math.cos(roll * 0.5), math.sin(roll * 0.5)
    cp, sp = math.cos(pitch * 0.5), math.sin(pitch * 0.5)
    cy, sy = math.cos(yaw * 0.5), math.sin(yaw * 0.5)
    return normalize_quat((
        sr * cp * cy - cr * sp * sy,
        cr * sp * cy + sr * cp * sy,
        cr * cp * sy - sr * sp * cy,
        cr * cp * cy + sr * sp * sy,
    ))


def quat_from_msg(msg_q) -> Quat:
    return normalize_quat((msg_q.x, msg_q.y, msg_q.z, msg_q.w))


def transform_to_rt(transform_msg) -> Tuple[Mat3, Vec3]:
    t = transform_msg.transform.translation
    q = transform_msg.transform.rotation
    return quat_to_matrix((q.x, q.y, q.z, q.w)), (t.x, t.y, t.z)


def invert_rt(rotation: Mat3, translation: Vec3) -> Tuple[Mat3, Vec3]:
    inv_r = mat_transpose(rotation)
    inv_t = mat_vec_mul(inv_r, neg_vec(translation))
    return inv_r, inv_t


def bool_param(node: Node, name: str, default: bool) -> bool:
    node.declare_parameter(name, default)
    value = node.get_parameter(name).value
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ('true', '1', 'yes', 'y', 'on')
    return bool(value)


def int_param(node: Node, name: str, default: int) -> int:
    node.declare_parameter(name, default)
    return int(node.get_parameter(name).value)


def float_param(node: Node, name: str, default: float) -> float:
    node.declare_parameter(name, default)
    return float(node.get_parameter(name).value)


def str_param(node: Node, name: str, default: str) -> str:
    node.declare_parameter(name, default)
    return str(node.get_parameter(name).value)


class ScanImuTiltCloud(Node):
    def __init__(self):
        super().__init__('scan_imu_tilt_cloud')

        self.scan_topic = str_param(self, 'scan_topic', '/scan')
        self.imu_topic = str_param(self, 'imu_topic', '/imu')
        self.tf_static_topic = str_param(self, 'tf_static_topic', '/tf_static')
        self.cloud_topic = str_param(self, 'cloud_topic', '/tilted_lidar_cloud')
        self.slice_topic = str_param(self, 'slice_topic', '/tilted_lidar_slice')
        self.world_frame = str_param(self, 'world_frame', 'base_link')
        self.base_frame = str_param(self, 'base_frame', 'base_link')
        self.accumulate = bool_param(self, 'accumulate', True)
        self.max_points = max(1000, int_param(self, 'max_points', 120000))
        self.point_stride = max(1, int_param(self, 'point_stride', 1))
        self.publish_every_n_scans = max(1, int_param(self, 'publish_every_n_scans', 1))
        self.use_roll_pitch_only = bool_param(self, 'use_roll_pitch_only', True)
        self.zero_initial_orientation = bool_param(self, 'zero_initial_orientation', True)
        self.invert_imu_rotation = bool_param(self, 'invert_imu_rotation', False)
        self.height_scale = float_param(self, 'height_scale', 1.0)
        self.preserve_lidar_range = bool_param(self, 'preserve_lidar_range', True)
        self.fixed_lidar_origin = bool_param(self, 'fixed_lidar_origin', True)
        self.min_range = float_param(self, 'min_range', 0.05)
        self.max_range = float_param(self, 'max_range', 8.0)
        self.publish_debug = bool_param(self, 'publish_debug', True)

        sensor_qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=20,
        )
        static_qos = QoSProfile(
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
        )

        self.static_transforms: Dict[TfKey, Tuple[Mat3, Vec3]] = {}
        self.latest_imu_q: Optional[Quat] = None
        self.initial_imu_q: Optional[Quat] = None
        self.accumulated: deque[Vec3] = deque(maxlen=self.max_points)
        self.scan_count = 0
        self.warned_tf_missing = False
        self.logged_tf_ok = False
        self.logged_first_cloud = False

        self.tf_static_sub = self.create_subscription(TFMessage, self.tf_static_topic, self.on_tf_static, static_qos)
        self.imu_sub = self.create_subscription(Imu, self.imu_topic, self.on_imu, sensor_qos)
        self.scan_sub = self.create_subscription(LaserScan, self.scan_topic, self.on_scan, sensor_qos)
        self.cloud_pub = self.create_publisher(PointCloud2, self.cloud_topic, 10)
        self.slice_pub = self.create_publisher(PointCloud2, self.slice_topic, 10)

        self.get_logger().info(
            'Tilted LiDAR mapper started. '
            f'scan={self.scan_topic}, imu={self.imu_topic}, cloud={self.cloud_topic}, '
            f'world_frame={self.world_frame}, base_frame={self.base_frame}, '
            f'accumulate={self.accumulate}, max_points={self.max_points}'
        )
        if abs(self.height_scale - 1.0) > 1e-9:
            self.get_logger().warn(
                'height_scale is not 1.0. This is a visual exaggeration and does not preserve the original LiDAR range.'
            )
        self.get_logger().info(
            'RViz2: set Fixed Frame to the selected world_frame and add PointCloud2 topic '
            f'"{self.cloud_topic}" or "{self.slice_topic}".'
        )

    def on_tf_static(self, msg: TFMessage) -> None:
        for transform in msg.transforms:
            parent = transform.header.frame_id.strip()
            child = transform.child_frame_id.strip()
            if not parent or not child:
                continue
            self.static_transforms[(parent, child)] = transform_to_rt(transform)

    def on_imu(self, msg: Imu) -> None:
        q = quat_from_msg(msg.orientation)
        if self.initial_imu_q is None:
            self.initial_imu_q = q
            if self.publish_debug:
                r, p, y = euler_from_quat(q)
                self.get_logger().info(
                    'Initial IMU orientation captured: '
                    f'roll={math.degrees(r):.1f} deg, '
                    f'pitch={math.degrees(p):.1f} deg, '
                    f'yaw={math.degrees(y):.1f} deg'
                )
        self.latest_imu_q = q

    def imu_rotation_matrix(self) -> Optional[Mat3]:
        if self.latest_imu_q is None:
            return None

        q = self.latest_imu_q
        if self.zero_initial_orientation and self.initial_imu_q is not None:
            # Relative orientation in the initial IMU frame: R_rel = R_initial.T @ R_current.
            q = quat_multiply(quat_conjugate(self.initial_imu_q), q)

        if self.invert_imu_rotation:
            q = quat_conjugate(q)

        if self.use_roll_pitch_only:
            roll, pitch, _yaw = euler_from_quat(q)
            q = quat_from_euler(roll, pitch, 0.0)

        return quat_to_matrix(q)

    def lookup_scan_to_base(self, scan_frame: str) -> Tuple[Mat3, Vec3]:
        if not scan_frame or scan_frame == self.base_frame:
            return quat_to_matrix((0.0, 0.0, 0.0, 1.0)), (0.0, 0.0, 0.0)

        direct_key = (self.base_frame, scan_frame)
        if direct_key in self.static_transforms:
            if not self.logged_tf_ok:
                self.get_logger().info(f'Using static TF: {self.base_frame} <- {scan_frame}')
                self.logged_tf_ok = True
            return self.static_transforms[direct_key]

        inverse_key = (scan_frame, self.base_frame)
        if inverse_key in self.static_transforms:
            if not self.logged_tf_ok:
                self.get_logger().info(f'Using inverse static TF: {self.base_frame} <- {scan_frame}')
                self.logged_tf_ok = True
            rotation, translation = self.static_transforms[inverse_key]
            return invert_rt(rotation, translation)

        if not self.warned_tf_missing:
            self.get_logger().warn(
                f'Static TF {self.base_frame} <- {scan_frame} has not been received. Using identity fallback.'
            )
            self.warned_tf_missing = True
        return quat_to_matrix((0.0, 0.0, 0.0, 1.0)), (0.0, 0.0, 0.0)

    def on_scan(self, msg: LaserScan) -> None:
        self.scan_count += 1
        if self.latest_imu_q is None:
            if self.scan_count % 30 == 1:
                self.get_logger().warn('Waiting for IMU data before converting scans...')
            return

        imu_R = self.imu_rotation_matrix()
        if imu_R is None:
            return

        scan_R, scan_t = self.lookup_scan_to_base(msg.header.frame_id)

        points: List[Vec3] = []
        range_min = max(self.min_range, msg.range_min if math.isfinite(msg.range_min) else self.min_range)
        range_max = min(self.max_range, msg.range_max if math.isfinite(msg.range_max) else self.max_range)

        for i in range(0, len(msg.ranges), self.point_stride):
            r = msg.ranges[i]
            if not math.isfinite(r) or r < range_min or r > range_max:
                continue

            angle = msg.angle_min + float(i) * msg.angle_increment
            p_scan = (r * math.cos(angle), r * math.sin(angle), 0.0)

            # Preserve the original LaserScan range by rotating the ray vector only.
            # The LiDAR origin offset is added separately after the ray rotation.
            v_base = mat_vec_mul(scan_R, p_scan)

            if self.preserve_lidar_range:
                v_world = mat_vec_mul(imu_R, v_base)
                origin_world = scan_t if self.fixed_lidar_origin else mat_vec_mul(imu_R, scan_t)
                p_world = add_vec(origin_world, v_world)
            else:
                p_base = add_vec(v_base, scan_t)
                p_world = mat_vec_mul(imu_R, p_base)

            if self.height_scale != 1.0:
                p_world = (p_world[0], p_world[1], p_world[2] * self.height_scale)
            points.append(p_world)

        if not points:
            return

        if self.accumulate:
            self.accumulated.extend(points)

        if self.scan_count % self.publish_every_n_scans != 0:
            return

        header = Header()
        header.stamp = msg.header.stamp
        header.frame_id = self.world_frame

        slice_msg = point_cloud2.create_cloud_xyz32(header, points)
        self.slice_pub.publish(slice_msg)

        cloud_points: Iterable[Vec3] = list(self.accumulated) if self.accumulate else points
        cloud_msg = point_cloud2.create_cloud_xyz32(header, cloud_points)
        self.cloud_pub.publish(cloud_msg)

        if self.publish_debug and not self.logged_first_cloud:
            self.get_logger().info(
                f'Published first cloud: current_slice={len(points)} points, '
                f'accumulated={len(self.accumulated) if self.accumulate else len(points)} points, '
                f'preserve_lidar_range={self.preserve_lidar_range}, '
                f'fixed_lidar_origin={self.fixed_lidar_origin}'
            )
            self.logged_first_cloud = True


def main(args: Optional[Sequence[str]] = None) -> None:
    rclpy.init(args=args)
    node = ScanImuTiltCloud()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
