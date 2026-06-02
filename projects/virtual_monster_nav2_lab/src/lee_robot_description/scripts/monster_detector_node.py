#!/usr/bin/env python3

import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import rclpy
import tf2_ros
import yaml
from ament_index_python.packages import get_package_share_directory
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


Point2 = Tuple[float, float]


@dataclass
class Cluster:
    points: List[Point2]

    @property
    def center(self) -> Point2:
        if not self.points:
            return 0.0, 0.0
        x_sum = sum(point[0] for point in self.points)
        y_sum = sum(point[1] for point in self.points)
        count = float(len(self.points))
        return x_sum / count, y_sum / count


class OccupancyMap:
    """Small dependency-free reader for ROS map_server YAML + PGM maps."""

    def __init__(self, map_yaml: str, logger):
        self.map_yaml = map_yaml
        self.logger = logger
        self.image_path = ''
        self.resolution = 0.05
        self.origin = (0.0, 0.0, 0.0)
        self.negate = 0
        self.occupied_thresh = 0.65
        self.free_thresh = 0.25
        self.width = 0
        self.height = 0
        self.pixels: List[int] = []
        self._load()

    def _load(self) -> None:
        with open(self.map_yaml, 'r', encoding='utf-8') as stream:
            data = yaml.safe_load(stream) or {}
        if not isinstance(data, dict):
            raise ValueError(f'Map yaml must contain a YAML map: {self.map_yaml}')

        image_value = str(data.get('image', '')).strip()
        if not image_value:
            raise ValueError(f'Map yaml has no image field: {self.map_yaml}')

        self.image_path = image_value
        if not os.path.isabs(self.image_path):
            self.image_path = os.path.join(os.path.dirname(self.map_yaml), self.image_path)

        self.resolution = float(data.get('resolution', self.resolution))
        origin = data.get('origin', list(self.origin))
        if not isinstance(origin, list) or len(origin) < 2:
            raise ValueError(f'Map yaml origin must be [x, y, yaw]: {self.map_yaml}')
        self.origin = (
            float(origin[0]),
            float(origin[1]),
            float(origin[2]) if len(origin) > 2 else 0.0,
        )
        self.negate = int(data.get('negate', self.negate))
        self.occupied_thresh = float(data.get('occupied_thresh', self.occupied_thresh))
        self.free_thresh = float(data.get('free_thresh', self.free_thresh))
        self.width, self.height, self.pixels = self._read_pgm(self.image_path)
        self.logger.info(
            f'Loaded detector occupancy map: {self.map_yaml} '
            f'({self.width}x{self.height}, resolution={self.resolution:.3f}m)'
        )

    def _read_token(self, data: bytes, index: int) -> Tuple[str, int]:
        length = len(data)
        while index < length:
            value = data[index]
            if value in b' \t\r\n':
                index += 1
                continue
            if value == ord('#'):
                while index < length and data[index] not in b'\r\n':
                    index += 1
                continue
            break

        start = index
        while index < length and data[index] not in b' \t\r\n':
            index += 1
        return data[start:index].decode('ascii'), index

    def _read_pgm(self, image_path: str) -> Tuple[int, int, List[int]]:
        with open(image_path, 'rb') as stream:
            data = stream.read()
        index = 0
        magic, index = self._read_token(data, index)
        if magic != 'P5':
            raise ValueError(f'Only binary PGM(P5) maps are supported: {image_path}')
        width_text, index = self._read_token(data, index)
        height_text, index = self._read_token(data, index)
        max_value_text, index = self._read_token(data, index)
        width = int(width_text)
        height = int(height_text)
        max_value = int(max_value_text)
        if max_value <= 0 or max_value > 255:
            raise ValueError(f'Only 8-bit PGM maps are supported: {image_path}')
        while index < len(data) and data[index] in b' \t\r\n':
            index += 1
        expected_size = width * height
        image_data = data[index:index + expected_size]
        if len(image_data) != expected_size:
            raise ValueError(
                f'PGM data size mismatch: expected {expected_size}, got {len(image_data)}'
            )
        return width, height, list(image_data)

    def world_to_map(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        origin_x, origin_y, _ = self.origin
        mx = int(math.floor((x - origin_x) / self.resolution))
        my_ros = int(math.floor((y - origin_y) / self.resolution))
        if mx < 0 or my_ros < 0 or mx >= self.width or my_ros >= self.height:
            return None
        row = self.height - 1 - my_ros
        return mx, row

    def _pixel(self, mx: int, row: int) -> int:
        return self.pixels[row * self.width + mx]

    def occupancy_probability(self, mx: int, row: int) -> float:
        pixel = self._pixel(mx, row)
        if self.negate:
            return float(pixel) / 255.0
        return (255.0 - float(pixel)) / 255.0

    def is_unknown_cell(self, mx: int, row: int) -> bool:
        # ROS map_server trinary PGM maps commonly encode unknown cells as 205.
        return abs(self._pixel(mx, row) - 205) <= 1

    def is_free_world(self, x: float, y: float, unknown_is_blocked: bool) -> bool:
        cell = self.world_to_map(x, y)
        if cell is None:
            return False
        mx, row = cell
        if unknown_is_blocked and self.is_unknown_cell(mx, row):
            return False
        probability = self.occupancy_probability(mx, row)
        if probability >= self.occupied_thresh:
            return False
        if unknown_is_blocked and probability > self.free_thresh:
            return False
        return True


class MonsterDetectorNode(Node):
    """Stage 4 detector.

    This node does not subscribe to /virtual_monster_states. It treats scan hits
    that fall on free static-map cells as dynamic obstacle / monster candidates.
    """

    def __init__(self):
        super().__init__('monster_detector_node')

        self.declare_parameter('scan_topic', '/lee/virtual_scan')
        self.declare_parameter('candidate_topic', '/lee/detected_monster_candidates')
        self.declare_parameter('map_frame', 'map_lee')
        self.declare_parameter('scan_frame', 'base_scan')
        self.declare_parameter('map_yaml', 'maps/slam_map.yaml')
        self.declare_parameter('unknown_is_blocked', True)
        self.declare_parameter('min_range', 0.12)
        self.declare_parameter('max_range', 1.40)
        self.declare_parameter('detection_fov_deg', 120.0)
        self.declare_parameter('cluster_distance', 0.30)
        self.declare_parameter('min_cluster_points', 3)
        self.declare_parameter('max_candidates', 3)
        self.declare_parameter('publish_empty', True)

        self.scan_topic = str(self.get_parameter('scan_topic').value)
        self.candidate_topic = str(self.get_parameter('candidate_topic').value)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.scan_frame = str(self.get_parameter('scan_frame').value)
        self.map_yaml = self._resolve_map_yaml(str(self.get_parameter('map_yaml').value))
        self.unknown_is_blocked = bool(self.get_parameter('unknown_is_blocked').value)
        self.min_range = float(self.get_parameter('min_range').value)
        self.max_range = float(self.get_parameter('max_range').value)
        self.detection_fov_deg = float(self.get_parameter('detection_fov_deg').value)
        self.cluster_distance = float(self.get_parameter('cluster_distance').value)
        self.min_cluster_points = int(self.get_parameter('min_cluster_points').value)
        self.max_candidates = int(self.get_parameter('max_candidates').value)
        self.publish_empty = bool(self.get_parameter('publish_empty').value)

        self.occupancy_map = OccupancyMap(self.map_yaml, self.get_logger())
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.candidate_pub = self.create_publisher(String, self.candidate_topic, 10)
        self.scan_sub = self.create_subscription(
            LaserScan,
            self.scan_topic,
            self._on_scan,
            qos_profile_sensor_data,
        )
        self.last_wait_log = None

        self.get_logger().info(
            'Monster detector ready: '
            f'scan_topic={self.scan_topic}, candidate_topic={self.candidate_topic}, '
            f'map_frame={self.map_frame}, scan_frame={self.scan_frame}, '
            f'max_range={self.max_range:.2f}m, fov={self.detection_fov_deg:.1f}deg'
        )

    def _resolve_map_yaml(self, path_text: str) -> str:
        path_text = os.path.expanduser(path_text)
        if os.path.isabs(path_text):
            return path_text
        try:
            package_share = get_package_share_directory('lee_robot_description')
            candidate = os.path.join(package_share, path_text)
            if os.path.exists(candidate):
                return candidate
        except Exception:
            pass
        return path_text

    def _on_scan(self, scan: LaserScan) -> None:
        source_frame = scan.header.frame_id or self.scan_frame
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                source_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except Exception as exc:
            self._log_waiting(f'waiting for TF {self.map_frame} -> {source_frame}: {exc}')
            return

        candidate_points: List[Point2] = []
        max_range = min(self.max_range, scan.range_max if scan.range_max > 0.0 else self.max_range)
        min_range = max(self.min_range, scan.range_min if scan.range_min > 0.0 else self.min_range)
        half_fov_rad = math.radians(max(0.0, min(360.0, self.detection_fov_deg)) * 0.5)
        use_fov_filter = half_fov_rad < math.pi

        for index, range_value in enumerate(scan.ranges):
            if not math.isfinite(range_value):
                continue
            if range_value < min_range or range_value > max_range:
                continue
            angle = scan.angle_min + float(index) * scan.angle_increment
            if use_fov_filter and abs(self._normalize_angle(angle)) > half_fov_rad:
                continue
            local_x = math.cos(angle) * range_value
            local_y = math.sin(angle) * range_value
            map_x, map_y, _ = self._transform_point(local_x, local_y, 0.0, transform)
            if self.occupancy_map.is_free_world(map_x, map_y, self.unknown_is_blocked):
                candidate_points.append((map_x, map_y))

        robot_position = (
            float(transform.transform.translation.x),
            float(transform.transform.translation.y),
        )
        clusters = self._cluster_points(candidate_points)
        candidates = self._clusters_to_candidates(clusters, robot_position)
        if candidates or self.publish_empty:
            self._publish_candidates(scan, candidates)

    def _cluster_points(self, points: List[Point2]) -> List[Cluster]:
        clusters: List[Cluster] = []
        for point in points:
            assigned_cluster = None
            for cluster in clusters:
                center = cluster.center
                if math.hypot(point[0] - center[0], point[1] - center[1]) <= self.cluster_distance:
                    assigned_cluster = cluster
                    break
            if assigned_cluster is None:
                clusters.append(Cluster(points=[point]))
            else:
                assigned_cluster.points.append(point)
        return [cluster for cluster in clusters if len(cluster.points) >= self.min_cluster_points]

    def _clusters_to_candidates(self, clusters: List[Cluster], robot_position: Point2) -> List[Dict]:
        candidates = []
        for index, cluster in enumerate(clusters):
            center = cluster.center
            robot_distance = self._distance(robot_position, center)
            candidates.append({
                'id': int(index),
                'x': float(center[0]),
                'y': float(center[1]),
                'point_count': int(len(cluster.points)),
                'confidence': float(min(1.0, len(cluster.points) / 10.0)),
                'robot_distance': float(robot_distance),
            })
        candidates.sort(key=lambda item: (item['robot_distance'], -item['point_count']))
        return candidates[:max(1, self.max_candidates)]


    def _distance(self, a: Point2, b: Point2) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    def _normalize_angle(self, angle: float) -> float:
        while angle > math.pi:
            angle -= 2.0 * math.pi
        while angle < -math.pi:
            angle += 2.0 * math.pi
        return angle

    def _publish_candidates(self, scan: LaserScan, candidates: List[Dict]) -> None:
        now = self.get_clock().now()
        payload = {
            'stamp': {
                'sec': int(now.nanoseconds // 1_000_000_000),
                'nanosec': int(now.nanoseconds % 1_000_000_000),
            },
            'frame_id': self.map_frame,
            'source_scan_topic': self.scan_topic,
            'source_scan_frame': scan.header.frame_id or self.scan_frame,
            'candidate_count': len(candidates),
            'candidates': candidates,
        }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
        self.candidate_pub.publish(message)

    def _log_waiting(self, message: str) -> None:
        now = self.get_clock().now()
        if self.last_wait_log is not None:
            elapsed = (now - self.last_wait_log).nanoseconds * 1.0e-9
            if elapsed < 3.0:
                return
        self.last_wait_log = now
        self.get_logger().info(message)

    def _transform_point(self, x: float, y: float, z: float, transform) -> Tuple[float, float, float]:
        translation = transform.transform.translation
        rotation = transform.transform.rotation

        xx = rotation.x * rotation.x
        yy = rotation.y * rotation.y
        zz = rotation.z * rotation.z
        xy = rotation.x * rotation.y
        xz = rotation.x * rotation.z
        yz = rotation.y * rotation.z
        wx = rotation.w * rotation.x
        wy = rotation.w * rotation.y
        wz = rotation.w * rotation.z

        rotated_x = (1.0 - 2.0 * (yy + zz)) * x + 2.0 * (xy - wz) * y + 2.0 * (xz + wy) * z
        rotated_y = 2.0 * (xy + wz) * x + (1.0 - 2.0 * (xx + zz)) * y + 2.0 * (yz - wx) * z
        rotated_z = 2.0 * (xz - wy) * x + 2.0 * (yz + wx) * y + (1.0 - 2.0 * (xx + yy)) * z

        return (
            rotated_x + translation.x,
            rotated_y + translation.y,
            rotated_z + translation.z,
        )


def main(args=None):
    rclpy.init(args=args)
    node = MonsterDetectorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
