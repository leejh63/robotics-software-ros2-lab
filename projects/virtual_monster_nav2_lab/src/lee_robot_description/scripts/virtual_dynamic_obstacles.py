#!/usr/bin/env python3

import json
import math
import os
import random
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import rclpy
import tf2_ros
import yaml
from rcl_interfaces.msg import SetParametersResult
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String
from std_srvs.srv import Trigger
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker, MarkerArray


Point2 = Tuple[float, float]


@dataclass
class VirtualObstacle:
    name: str
    shape: str
    radius: float
    height: float
    speed: float
    mode: str
    path: List[Point2]
    position: Point2
    target_index: int = 1
    direction: int = 1
    clearable: bool = True
    alive: bool = True
    random_motion: bool = False
    target: Optional[Point2] = None

    def step(self, dt: float) -> None:
        if self.random_motion:
            return
        if not self.alive:
            return
        if dt <= 0.0 or self.speed <= 0.0 or len(self.path) < 2:
            return

        remaining = self.speed * dt
        while remaining > 0.0:
            target = self.path[self.target_index]
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            distance = math.hypot(dx, dy)

            if distance <= 1.0e-9:
                if self._at_final_once_target():
                    return
                self._advance_target()
                continue

            if remaining < distance:
                ratio = remaining / distance
                self.position = (
                    self.position[0] + dx * ratio,
                    self.position[1] + dy * ratio,
                )
                return

            self.position = target
            remaining -= distance
            if self._at_final_once_target():
                return
            self._advance_target()

    def _at_final_once_target(self) -> bool:
        return self.mode == 'once' and self.target_index == len(self.path) - 1

    def _advance_target(self) -> None:
        if self.mode == 'loop':
            self.target_index = (self.target_index + 1) % len(self.path)
            return

        if self.mode == 'once':
            self.target_index = min(self.target_index + 1, len(self.path) - 1)
            return

        next_index = self.target_index + self.direction
        if next_index >= len(self.path) or next_index < 0:
            self.direction *= -1
            next_index = self.target_index + self.direction

        self.target_index = next_index


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

        if self.resolution <= 0.0:
            raise ValueError('Map resolution must be positive.')
        if self.width <= 0 or self.height <= 0:
            raise ValueError('Map image size must be positive.')

        self.logger.info(
            f'Loaded occupancy map: {self.map_yaml} '
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

    def map_to_world(self, mx: int, row: int) -> Point2:
        origin_x, origin_y, _ = self.origin
        my_ros = self.height - 1 - row
        x = origin_x + (float(mx) + 0.5) * self.resolution
        y = origin_y + (float(my_ros) + 0.5) * self.resolution
        return x, y

    def _pixel(self, mx: int, row: int) -> int:
        return self.pixels[row * self.width + mx]

    def occupancy_probability(self, mx: int, row: int) -> float:
        pixel = self._pixel(mx, row)
        if self.negate:
            return float(pixel) / 255.0
        return (255.0 - float(pixel)) / 255.0

    def is_free_cell(self, mx: int, row: int, unknown_is_blocked: bool) -> bool:
        if mx < 0 or row < 0 or mx >= self.width or row >= self.height:
            return False
        probability = self.occupancy_probability(mx, row)
        if probability >= self.occupied_thresh:
            return False
        if unknown_is_blocked and probability > self.free_thresh:
            return False
        return True


class VirtualDynamicObstacles(Node):
    def __init__(self):
        super().__init__('virtual_dynamic_obstacles')

        self.declare_parameter('config_file', '')
        self.declare_parameter('obstacle_frame', '')
        self.declare_parameter('scan_frame', '')
        self.declare_parameter('scan_topic', '')
        self.declare_parameter('marker_topic', '')
        self.declare_parameter('state_topic', '')
        self.declare_parameter('clear_service_name', '')
        self.declare_parameter('reset_service_name', '')
        self.declare_parameter('target_count', -1)

        self.config_file = ''
        self.config = self._load_config()
        self.random = random.Random()

        self.obstacle_frame = self._string_param(
            'obstacle_frame',
            self.config.get('obstacle_frame', 'map_lee'),
        )
        self.scan_frame = self._string_param(
            'scan_frame',
            self.config.get('scan_frame', 'base_scan'),
        )
        self.scan_topic = self._string_param(
            'scan_topic',
            self.config.get('scan_topic', '/lee/virtual_scan'),
        )
        self.marker_topic = self._string_param(
            'marker_topic',
            self.config.get('marker_topic', '/lee/virtual_obstacle_markers'),
        )
        self.state_topic = self._string_param(
            'state_topic',
            self.config.get('state_topic', '/lee/virtual_monster_states'),
        )

        self.clear_rule = self.config.get('clear_rule', {}) or {}
        if not isinstance(self.clear_rule, dict):
            raise ValueError('clear_rule must be a YAML map.')

        self.clear_enabled = bool(self.clear_rule.get('enabled', True))
        self.clear_service_name = self._string_param(
            'clear_service_name',
            str(self.clear_rule.get('service_name', '/lee/clear_nearest_virtual_obstacle')),
        )
        self.attack_range = self._float_from_map(
            self.clear_rule, 'attack_range', 0.70, minimum=0.01
        )
        self.attack_fov_rad = math.radians(
            self._float_from_map(self.clear_rule, 'attack_fov_deg', 60.0, minimum=1.0)
        )
        self.attack_cooldown = self._float_from_map(
            self.clear_rule, 'attack_cooldown', 1.0, minimum=0.0
        )
        self.last_clear_stamp: Optional[Time] = None
        self.last_removed_stamp: Optional[Time] = None
        self.last_status_log_stamp: Optional[Time] = None

        self.update_rate = self._float_config('update_rate', 10.0, minimum=0.1)
        self.sample_count = int(self._float_config('sample_count', 360, minimum=16))
        self.angle_min = self._float_config('angle_min', -math.pi)
        configured_angle_max = self.config.get('angle_max')
        if configured_angle_max is None:
            self.angle_increment = (2.0 * math.pi) / float(self.sample_count)
            self.angle_max = self.angle_min + self.angle_increment * (self.sample_count - 1)
        else:
            self.angle_max = float(configured_angle_max)
            self.angle_increment = (
                (self.angle_max - self.angle_min) / float(max(1, self.sample_count - 1))
            )

        self.range_min = self._float_config('range_min', 0.12, minimum=0.0)
        self.range_max = self._float_config('range_max', 3.5, minimum=self.range_min)
        self.default_height = self._float_config('default_height', 0.6, minimum=0.01)

        self.marker_style = self.config.get('marker_style', {}) or {}
        if not isinstance(self.marker_style, dict):
            raise ValueError('marker_style must be a YAML map.')
        self.marker_body_type = str(self.marker_style.get('body_type', 'sphere')).lower()
        if self.marker_body_type not in ('sphere', 'cylinder', 'cube'):
            self.get_logger().warn(
                f'marker_style.body_type="{self.marker_body_type}" is invalid. Using sphere.'
            )
            self.marker_body_type = 'sphere'
        self.marker_body_radius_scale = self._float_from_map(
            self.marker_style,
            'body_radius_scale',
            0.55,
            minimum=0.05,
        )
        self.marker_body_alpha = self._float_from_map(self.marker_style, 'body_alpha', 0.95, minimum=0.0)
        self.show_collision_radius = bool(self.marker_style.get('show_collision_radius', True))
        self.collision_radius_alpha = self._float_from_map(
            self.marker_style,
            'collision_radius_alpha',
            0.18,
            minimum=0.0,
        )
        self.show_target_line = bool(self.marker_style.get('show_target_line', False))

        self.map_filter = self.config.get('map_filter', {}) or {}
        if not isinstance(self.map_filter, dict):
            raise ValueError('map_filter must be a YAML map.')

        self.random_spawn = self.config.get('random_spawn', {}) or {}
        if not isinstance(self.random_spawn, dict):
            raise ValueError('random_spawn must be a YAML map.')
        self.random_spawn_enabled = bool(self.random_spawn.get('enabled', False))
        yaml_target_count = int(self._float_from_map(self.random_spawn, 'target_count', 3, minimum=0))
        param_target_count = self._int_param('target_count', -1)
        self.target_count = param_target_count if param_target_count >= 0 else yaml_target_count
        if param_target_count < 0:
            self.set_parameters([
                Parameter('target_count', Parameter.Type.INTEGER, self.target_count),
            ])
        self.respawn_delay = self._float_from_map(self.random_spawn, 'respawn_delay', 0.0, minimum=0.0)
        self.radius_min = self._float_from_map(self.random_spawn, 'radius_min', 0.25, minimum=0.01)
        self.radius_max = self._float_from_map(self.random_spawn, 'radius_max', 0.35, minimum=self.radius_min)
        self.speed_min = self._float_from_map(self.random_spawn, 'speed_min', 0.12, minimum=0.0)
        self.speed_max = self._float_from_map(self.random_spawn, 'speed_max', 0.28, minimum=self.speed_min)
        self.wall_clearance = self._float_from_map(self.random_spawn, 'wall_clearance', 0.25, minimum=0.0)
        self.robot_spawn_clearance = self._float_from_map(self.random_spawn, 'robot_spawn_clearance', 1.0, minimum=0.0)
        self.monster_clearance = self._float_from_map(self.random_spawn, 'monster_clearance', 0.60, minimum=0.0)
        self.target_min_distance = self._float_from_map(self.random_spawn, 'target_min_distance', 0.80, minimum=0.0)
        self.target_max_distance = self._float_from_map(self.random_spawn, 'target_max_distance', 2.0, minimum=self.target_min_distance)
        self.max_spawn_attempts = int(self._float_from_map(self.random_spawn, 'max_spawn_attempts', 200, minimum=1))
        self.max_target_attempts = int(self._float_from_map(self.random_spawn, 'max_target_attempts', 100, minimum=1))
        self.path_check_step = self._float_from_map(self.random_spawn, 'path_check_step', 0.05, minimum=0.01)
        self.require_robot_tf_for_spawn = bool(self.random_spawn.get('require_robot_tf_for_spawn', True))
        seed = self.random_spawn.get('seed')
        if seed is not None:
            self.random.seed(int(seed))

        self.occupancy_map: Optional[OccupancyMap] = None
        self.unknown_is_blocked = bool(self.map_filter.get('unknown_is_blocked', True))
        if self.random_spawn_enabled or bool(self.map_filter.get('enabled', False)):
            map_yaml = self._resolve_path(str(self.map_filter.get('map_yaml', 'maps/slam_map.yaml')))
            self.occupancy_map = OccupancyMap(map_yaml, self.get_logger())

        if self.random_spawn_enabled:
            self.obstacles: List[VirtualObstacle] = []
        else:
            self.obstacles = self._load_obstacles(self.config.get('obstacles', []))
            if not self.obstacles:
                raise ValueError('At least one virtual obstacle must be configured.')

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.scan_pub = self.create_publisher(
            LaserScan,
            self.scan_topic,
            qos_profile_sensor_data,
        )
        self.marker_pub = self.create_publisher(MarkerArray, self.marker_topic, 10)
        self.state_pub = self.create_publisher(String, self.state_topic, 10)

        self.clear_srv = None
        if self.clear_enabled:
            self.clear_srv = self.create_service(
                Trigger,
                self.clear_service_name,
                self._handle_clear_nearest_obstacle,
            )

        reset_service_fallback = self._default_reset_service_name(self.clear_service_name)
        self.reset_service_name = self._string_param('reset_service_name', reset_service_fallback)
        self.reset_srv = self.create_service(
            Trigger,
            self.reset_service_name,
            self._handle_reset_random_obstacles,
        )
        self.add_on_set_parameters_callback(self._on_parameter_update)

        self.last_stamp: Optional[Time] = None
        self.missing_tf_count = 0
        self.missing_robot_tf_count = 0
        self.failed_spawn_count = 0
        self.timer = self.create_timer(1.0 / self.update_rate, self._on_timer)

        mode_text = 'random-map-spawn' if self.random_spawn_enabled else 'fixed-path'
        self.get_logger().info(
            'Virtual dynamic obstacles: '
            f'mode={mode_text}, {self.obstacle_frame} -> {self.scan_frame}, '
            f'{self.scan_topic}, {len(self.obstacles)} initial obstacle(s)'
        )
        if self.random_spawn_enabled:
            self.get_logger().info(
                'Random virtual monster rule: '
                f'target_count={self.target_count}, '
                f'radius={self.radius_min:.2f}-{self.radius_max:.2f}m, '
                f'speed={self.speed_min:.2f}-{self.speed_max:.2f}m/s, '
                f'wall_clearance={self.wall_clearance:.2f}m, '
                f'robot_spawn_clearance={self.robot_spawn_clearance:.2f}m'
            )
        if self.clear_enabled:
            self.get_logger().info(
                'Virtual obstacle clear service: '
                f'{self.clear_service_name}, '
                f'range={self.attack_range:.2f}m, '
                f'fov={math.degrees(self.attack_fov_rad):.1f}deg'
            )
        self.get_logger().info(
            f'Virtual monster reset service: {self.reset_service_name}. '
            'Runtime target count can be changed with parameter "target_count".'
        )
        self.get_logger().info(f'Virtual monster state topic: {self.state_topic}')

    def _load_config(self) -> Dict:
        config_file = self.get_parameter('config_file').value
        if not config_file:
            return {}

        self.config_file = str(config_file)
        with open(self.config_file, 'r', encoding='utf-8') as stream:
            data = yaml.safe_load(stream) or {}

        if not isinstance(data, dict):
            raise ValueError(f'Config file must contain a YAML map: {self.config_file}')

        return data

    def _resolve_path(self, path_text: str) -> str:
        path_text = os.path.expanduser(path_text)
        if os.path.isabs(path_text):
            return path_text

        if self.config_file:
            candidate = os.path.join(os.path.dirname(self.config_file), path_text)
            if os.path.exists(candidate):
                return candidate

            package_candidate = os.path.join(
                os.path.dirname(os.path.dirname(self.config_file)),
                path_text,
            )
            if os.path.exists(package_candidate):
                return package_candidate

        return path_text

    def _string_param(self, name: str, fallback: str) -> str:
        value = self.get_parameter(name).value
        if isinstance(value, str) and value:
            return value
        return fallback

    def _int_param(self, name: str, fallback: int) -> int:
        value = self.get_parameter(name).value
        if value is None:
            return fallback
        try:
            return int(value)
        except (TypeError, ValueError):
            self.get_logger().warn(
                f'Parameter {name}={value!r} is not an integer. Falling back to {fallback}.'
            )
            return fallback

    def _default_reset_service_name(self, clear_service_name: str) -> str:
        if clear_service_name.endswith('/clear_nearest_virtual_obstacle'):
            return clear_service_name[: -len('/clear_nearest_virtual_obstacle')] + '/reset_virtual_obstacles'
        return '/reset_virtual_obstacles'

    def _float_config(
        self,
        name: str,
        fallback: float,
        minimum: Optional[float] = None,
    ) -> float:
        return self._float_from_map(self.config, name, fallback, minimum)

    def _float_from_map(
        self,
        source: Dict,
        name: str,
        fallback: float,
        minimum: Optional[float] = None,
    ) -> float:
        value = float(source.get(name, fallback))
        if minimum is not None and value < minimum:
            self.get_logger().warn(
                f'{name}={value} is below {minimum}. Falling back to {fallback}.'
            )
            return float(fallback)
        return value

    def _load_obstacles(self, entries) -> List[VirtualObstacle]:
        if not isinstance(entries, list):
            raise ValueError('obstacles must be a list.')

        obstacles = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                raise ValueError(f'obstacles[{index}] must be a YAML map.')

            path = self._load_path(entry.get('path', []), index)
            radius = float(entry.get('radius', 0.3))
            if radius <= 0.0:
                raise ValueError(f'obstacles[{index}].radius must be positive.')

            mode = str(entry.get('loop', 'ping_pong'))
            if mode not in ('ping_pong', 'loop', 'once'):
                self.get_logger().warn(
                    f'obstacles[{index}].loop="{mode}" is invalid. Using ping_pong.'
                )
                mode = 'ping_pong'

            obstacles.append(
                VirtualObstacle(
                    name=str(entry.get('name', f'virtual_obstacle_{index + 1}')),
                    shape=str(entry.get('shape', 'circle')),
                    radius=radius,
                    height=float(entry.get('height', self.default_height)),
                    speed=float(entry.get('speed', 0.0)),
                    mode=mode,
                    path=path,
                    position=path[0],
                    target_index=1 if len(path) > 1 else 0,
                    clearable=bool(entry.get('clearable', True)),
                    alive=bool(entry.get('alive', True)),
                )
            )

        return obstacles

    def _load_path(self, path, obstacle_index: int) -> List[Point2]:
        if not isinstance(path, list) or not path:
            raise ValueError(f'obstacles[{obstacle_index}].path must not be empty.')

        points = []
        for point_index, point in enumerate(path):
            if not isinstance(point, list) or len(point) < 2:
                raise ValueError(
                    f'obstacles[{obstacle_index}].path[{point_index}] must be [x, y].'
                )
            points.append((float(point[0]), float(point[1])))

        return points

    def _on_timer(self) -> None:
        now = self.get_clock().now()
        dt = self._compute_dt(now)

        if self.random_spawn_enabled:
            self._maintain_random_obstacles(now)
            self._step_random_obstacles(dt)
            self._log_random_status_periodically(now)
        else:
            for obstacle in self.obstacles:
                obstacle.step(dt)

        self._publish_markers(now)
        self._publish_monster_states(now)

        try:
            transform = self.tf_buffer.lookup_transform(
                self.scan_frame,
                self.obstacle_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except Exception as exc:
            self.missing_tf_count += 1
            if self.missing_tf_count in (1, 20, 100):
                self.get_logger().warn(
                    f'Waiting for TF {self.obstacle_frame} -> {self.scan_frame}: {exc}'
                )
            return

        self.missing_tf_count = 0
        self._publish_scan(now, transform)

    def _compute_dt(self, now: Time) -> float:
        if self.last_stamp is None:
            self.last_stamp = now
            return 0.0

        dt = (now - self.last_stamp).nanoseconds * 1.0e-9
        self.last_stamp = now
        if dt < 0.0:
            return 0.0
        return min(dt, 0.5)

    def _on_parameter_update(self, parameters):
        for parameter in parameters:
            if parameter.name != 'target_count':
                continue

            try:
                new_target_count = int(parameter.value)
            except (TypeError, ValueError):
                return SetParametersResult(
                    successful=False,
                    reason='target_count must be an integer greater than or equal to 0.',
                )

            if new_target_count < 0:
                return SetParametersResult(
                    successful=False,
                    reason='target_count must be greater than or equal to 0.',
                )

            old_target_count = self.target_count
            self.target_count = new_target_count
            now = self.get_clock().now()
            if self.random_spawn_enabled:
                self._trim_random_obstacles_to_target_count(now)
                self._maintain_random_obstacles(now)
            self.get_logger().info(
                f'Changed random monster target_count: {old_target_count} -> {self.target_count}'
            )

        return SetParametersResult(successful=True)

    def _log_random_status_periodically(self, now: Time) -> None:
        if not self.random_spawn_enabled:
            return
        if self.last_status_log_stamp is not None:
            elapsed = (now - self.last_status_log_stamp).nanoseconds * 1.0e-9
            if elapsed < 5.0:
                return
        self.last_status_log_stamp = now
        alive_count = len(self._alive_random_obstacles())
        self.get_logger().debug(
            f'Random monster status: alive={alive_count}, target_count={self.target_count}'
        )

    def _trim_random_obstacles_to_target_count(self, now: Time) -> None:
        alive_random = self._alive_random_obstacles()
        extra_count = len(alive_random) - self.target_count
        if extra_count <= 0:
            return

        for obstacle in reversed(self.obstacles):
            if extra_count <= 0:
                break
            if not obstacle.alive or not obstacle.random_motion:
                continue
            obstacle_index = self.obstacles.index(obstacle)
            obstacle.alive = False
            obstacle.target = None
            self._publish_delete_marker(obstacle_index, now)
            extra_count -= 1

    def _alive_random_obstacles(self) -> List[VirtualObstacle]:
        return [obstacle for obstacle in self.obstacles if obstacle.alive and obstacle.random_motion]

    def _maintain_random_obstacles(self, now: Time) -> None:
        if not self.random_spawn_enabled:
            return
        if self.occupancy_map is None:
            return

        alive_count = len(self._alive_random_obstacles())
        if alive_count >= self.target_count:
            return

        if self.last_removed_stamp is not None and self.respawn_delay > 0.0:
            elapsed = (now - self.last_removed_stamp).nanoseconds * 1.0e-9
            if elapsed < self.respawn_delay:
                return

        robot_position = self._lookup_robot_position_in_obstacle_frame()
        if robot_position is None and self.require_robot_tf_for_spawn:
            self.missing_robot_tf_count += 1
            if self.missing_robot_tf_count in (1, 20, 100):
                self.get_logger().warn(
                    f'Waiting for robot TF {self.obstacle_frame} -> {self.scan_frame} '
                    'before random monster spawn.'
                )
            return
        self.missing_robot_tf_count = 0

        while len(self._alive_random_obstacles()) < self.target_count:
            obstacle = self._spawn_random_obstacle(robot_position)
            if obstacle is None:
                self.failed_spawn_count += 1
                if self.failed_spawn_count in (1, 20, 100):
                    self.get_logger().warn(
                        'Failed to spawn a random monster in a valid map area. '
                        'Check wall_clearance, robot_spawn_clearance, and map size.'
                    )
                return

            self.failed_spawn_count = 0
            self.obstacles.append(obstacle)
            self.get_logger().info(
                f'Spawned random monster "{obstacle.name}" '
                f'at x={obstacle.position[0]:.2f}, y={obstacle.position[1]:.2f}'
            )

    def _spawn_random_obstacle(self, robot_position: Optional[Point2]) -> Optional[VirtualObstacle]:
        radius = self.random.uniform(self.radius_min, self.radius_max)
        speed = self.random.uniform(self.speed_min, self.speed_max)

        for _ in range(self.max_spawn_attempts):
            position = self._sample_valid_map_position(radius)
            if position is None:
                continue
            if robot_position is not None:
                if self._distance(position, robot_position) < self.robot_spawn_clearance:
                    continue
            if not self._is_far_from_alive_obstacles(position, radius):
                continue

            obstacle_index = len(self.obstacles) + 1
            obstacle = VirtualObstacle(
                name=f'random_monster_{obstacle_index}',
                shape='circle',
                radius=radius,
                height=self.default_height,
                speed=speed,
                mode='random',
                path=[position],
                position=position,
                target_index=0,
                clearable=True,
                alive=True,
                random_motion=True,
                target=None,
            )
            obstacle.target = self._sample_random_target(obstacle)
            return obstacle

        return None

    def _sample_valid_map_position(self, radius: float) -> Optional[Point2]:
        if self.occupancy_map is None:
            return None

        for _ in range(self.max_spawn_attempts):
            mx = self.random.randrange(0, self.occupancy_map.width)
            row = self.random.randrange(0, self.occupancy_map.height)
            position = self.occupancy_map.map_to_world(mx, row)
            if self._is_valid_monster_position(position, radius):
                return position

        return None

    def _sample_random_target(self, obstacle: VirtualObstacle) -> Optional[Point2]:
        for _ in range(self.max_target_attempts):
            angle = self.random.uniform(-math.pi, math.pi)
            distance = self.random.uniform(self.target_min_distance, self.target_max_distance)
            target = (
                obstacle.position[0] + math.cos(angle) * distance,
                obstacle.position[1] + math.sin(angle) * distance,
            )

            if not self._is_valid_monster_position(target, obstacle.radius):
                continue
            if not self._line_is_valid(obstacle.position, target, obstacle.radius):
                continue
            return target

        return None

    def _step_random_obstacles(self, dt: float) -> None:
        if dt <= 0.0:
            return

        for obstacle in self._alive_random_obstacles():
            if obstacle.speed <= 0.0:
                continue

            if obstacle.target is None or self._distance(obstacle.position, obstacle.target) <= 0.08:
                obstacle.target = self._sample_random_target(obstacle)
                if obstacle.target is None:
                    continue

            dx = obstacle.target[0] - obstacle.position[0]
            dy = obstacle.target[1] - obstacle.position[1]
            distance = math.hypot(dx, dy)
            if distance <= 1.0e-9:
                obstacle.target = None
                continue

            step_distance = min(obstacle.speed * dt, distance)
            ratio = step_distance / distance
            next_position = (
                obstacle.position[0] + dx * ratio,
                obstacle.position[1] + dy * ratio,
            )

            if self._is_valid_monster_position(next_position, obstacle.radius):
                obstacle.position = next_position
            else:
                obstacle.target = None

    def _is_valid_monster_position(self, position: Point2, radius: float) -> bool:
        if self.occupancy_map is None:
            return True

        cell = self.occupancy_map.world_to_map(position[0], position[1])
        if cell is None:
            return False

        mx, row = cell
        clearance = radius + self.wall_clearance
        cell_radius = int(math.ceil(clearance / self.occupancy_map.resolution))

        for dy in range(-cell_radius, cell_radius + 1):
            for dx in range(-cell_radius, cell_radius + 1):
                if math.hypot(dx, dy) * self.occupancy_map.resolution > clearance:
                    continue
                check_x = mx + dx
                check_row = row + dy
                if not self.occupancy_map.is_free_cell(
                    check_x,
                    check_row,
                    self.unknown_is_blocked,
                ):
                    return False
        return True

    def _line_is_valid(self, start: Point2, end: Point2, radius: float) -> bool:
        distance = self._distance(start, end)
        steps = max(1, int(math.ceil(distance / self.path_check_step)))
        for index in range(steps + 1):
            ratio = float(index) / float(steps)
            point = (
                start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio,
            )
            if not self._is_valid_monster_position(point, radius):
                return False
        return True

    def _is_far_from_alive_obstacles(self, position: Point2, radius: float) -> bool:
        for obstacle in self.obstacles:
            if not obstacle.alive:
                continue
            required_distance = max(self.monster_clearance, radius + obstacle.radius)
            if self._distance(position, obstacle.position) < required_distance:
                return False
        return True

    def _lookup_robot_position_in_obstacle_frame(self) -> Optional[Point2]:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.obstacle_frame,
                self.scan_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except Exception:
            return None

        translation = transform.transform.translation
        return (float(translation.x), float(translation.y))

    def _distance(self, first: Point2, second: Point2) -> float:
        return math.hypot(first[0] - second[0], first[1] - second[1])

    def _publish_scan(self, stamp: Time, transform) -> None:
        scan = LaserScan()
        scan.header.stamp = stamp.to_msg()
        scan.header.frame_id = self.scan_frame
        scan.angle_min = self.angle_min
        scan.angle_max = self.angle_max
        scan.angle_increment = self.angle_increment
        scan.time_increment = 0.0
        scan.scan_time = 1.0 / self.update_rate
        scan.range_min = self.range_min
        scan.range_max = self.range_max
        scan.ranges = [math.inf] * self.sample_count
        scan.intensities = [0.0] * self.sample_count

        for obstacle in self.obstacles:
            if not obstacle.alive:
                continue
            x, y, _ = self._transform_point(
                obstacle.position[0],
                obstacle.position[1],
                0.0,
                transform,
            )
            self._mark_circle(scan, x, y, obstacle.radius)

        self.scan_pub.publish(scan)

    def _mark_circle(self, scan: LaserScan, center_x: float, center_y: float, radius: float) -> None:
        center_distance = math.hypot(center_x, center_y)
        if center_distance - radius > self.range_max:
            return
        if center_distance + radius < self.range_min:
            return

        for index in range(self.sample_count):
            angle = self.angle_min + index * self.angle_increment
            direction_x = math.cos(angle)
            direction_y = math.sin(angle)
            projection = center_x * direction_x + center_y * direction_y
            if projection <= 0.0:
                continue

            perpendicular_sq = center_distance * center_distance - projection * projection
            radius_sq = radius * radius
            if perpendicular_sq > radius_sq:
                continue

            hit_distance = projection - math.sqrt(max(0.0, radius_sq - perpendicular_sq))
            if hit_distance < self.range_min or hit_distance > self.range_max:
                continue

            if not math.isfinite(scan.ranges[index]) or hit_distance < scan.ranges[index]:
                scan.ranges[index] = hit_distance
                scan.intensities[index] = 1.0

    def _publish_markers(self, stamp: Time) -> None:
        marker_array = MarkerArray()
        for index, obstacle in enumerate(self.obstacles):
            if not obstacle.alive:
                continue

            body_marker = self._make_body_marker(index, obstacle, stamp)
            marker_array.markers.append(body_marker)

            if self.show_collision_radius:
                collision_marker = self._make_collision_radius_marker(index, obstacle, stamp)
                marker_array.markers.append(collision_marker)

            if self.show_target_line and obstacle.target is not None:
                target_marker = self._make_target_line_marker(index, obstacle, stamp)
                marker_array.markers.append(target_marker)

        self.marker_pub.publish(marker_array)

    def _publish_monster_states(self, stamp: Time) -> None:
        alive_obstacles = [obstacle for obstacle in self.obstacles if obstacle.alive]
        payload = {
            'stamp': {
                'sec': int(stamp.nanoseconds // 1_000_000_000),
                'nanosec': int(stamp.nanoseconds % 1_000_000_000),
            },
            'frame_id': self.obstacle_frame,
            'scan_frame': self.scan_frame,
            'mode': 'random-map-spawn' if self.random_spawn_enabled else 'fixed-path',
            'target_count': int(self.target_count) if self.random_spawn_enabled else len(alive_obstacles),
            'alive_count': len(alive_obstacles),
            'known_count': len(self.obstacles),
            'monsters': [
                self._monster_state_dict(index, obstacle)
                for index, obstacle in enumerate(self.obstacles)
                if obstacle.alive
            ],
        }
        message = String()
        message.data = json.dumps(payload, ensure_ascii=False, separators=(',', ':'))
        self.state_pub.publish(message)

    def _monster_state_dict(self, index: int, obstacle: VirtualObstacle) -> Dict:
        state = {
            'id': int(index),
            'name': obstacle.name,
            'x': float(obstacle.position[0]),
            'y': float(obstacle.position[1]),
            'radius': float(obstacle.radius),
            'height': float(obstacle.height),
            'speed': float(obstacle.speed),
            'alive': bool(obstacle.alive),
            'clearable': bool(obstacle.clearable),
            'random_motion': bool(obstacle.random_motion),
        }
        if obstacle.target is not None:
            state['target'] = {
                'x': float(obstacle.target[0]),
                'y': float(obstacle.target[1]),
            }
        else:
            state['target'] = None
        return state

    def _base_marker(self, index: int, sub_id: int, stamp: Time) -> Marker:
        marker = Marker()
        marker.header.stamp = stamp.to_msg()
        marker.header.frame_id = self.obstacle_frame
        marker.ns = 'virtual_dynamic_obstacles'
        marker.id = index * 10 + sub_id
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.lifetime = Duration(seconds=0.4).to_msg()
        return marker

    def _make_body_marker(self, index: int, obstacle: VirtualObstacle, stamp: Time) -> Marker:
        marker = self._base_marker(index, 0, stamp)
        if self.marker_body_type == 'cylinder':
            marker.type = Marker.CYLINDER
        elif self.marker_body_type == 'cube':
            marker.type = Marker.CUBE
        else:
            marker.type = Marker.SPHERE

        visual_radius = max(0.01, obstacle.radius * self.marker_body_radius_scale)
        visual_diameter = visual_radius * 2.0
        marker.pose.position.x = obstacle.position[0]
        marker.pose.position.y = obstacle.position[1]

        if marker.type == Marker.SPHERE:
            marker.pose.position.z = visual_radius
            marker.scale.x = visual_diameter
            marker.scale.y = visual_diameter
            marker.scale.z = visual_diameter
        else:
            marker.pose.position.z = obstacle.height * 0.5
            marker.scale.x = visual_diameter
            marker.scale.y = visual_diameter
            marker.scale.z = obstacle.height

        marker.color.r = 1.0
        marker.color.g = 0.20
        marker.color.b = 0.05
        marker.color.a = min(1.0, self.marker_body_alpha)
        return marker

    def _make_collision_radius_marker(self, index: int, obstacle: VirtualObstacle, stamp: Time) -> Marker:
        marker = self._base_marker(index, 1, stamp)
        marker.type = Marker.CYLINDER
        marker.pose.position.x = obstacle.position[0]
        marker.pose.position.y = obstacle.position[1]
        marker.pose.position.z = 0.01
        marker.scale.x = obstacle.radius * 2.0
        marker.scale.y = obstacle.radius * 2.0
        marker.scale.z = 0.02
        marker.color.r = 1.0
        marker.color.g = 0.55
        marker.color.b = 0.05
        marker.color.a = min(1.0, self.collision_radius_alpha)
        return marker

    def _make_target_line_marker(self, index: int, obstacle: VirtualObstacle, stamp: Time) -> Marker:
        marker = self._base_marker(index, 2, stamp)
        marker.type = Marker.LINE_STRIP
        marker.scale.x = 0.025
        start = Point()
        start.x = obstacle.position[0]
        start.y = obstacle.position[1]
        start.z = 0.08
        end = Point()
        end.x = obstacle.target[0]
        end.y = obstacle.target[1]
        end.z = 0.08
        marker.points = [start, end]
        marker.color.r = 1.0
        marker.color.g = 0.85
        marker.color.b = 0.05
        marker.color.a = 0.65
        return marker

    def _handle_reset_random_obstacles(self, request, response):
        del request

        if not self.random_spawn_enabled:
            response.success = False
            response.message = 'random_spawn.enabled is false; reset is only available in random spawn mode'
            return response

        now = self.get_clock().now()
        removed_count = 0
        for index, obstacle in enumerate(self.obstacles):
            if not obstacle.alive or not obstacle.random_motion:
                continue
            obstacle.alive = False
            obstacle.target = None
            self._publish_delete_marker(index, now)
            removed_count += 1

        self.last_removed_stamp = None
        self._maintain_random_obstacles(now)
        self._publish_monster_states(now)
        alive_count = len(self._alive_random_obstacles())
        self.get_logger().info(
            f'Reset random virtual monsters: removed={removed_count}, alive={alive_count}, target_count={self.target_count}'
        )
        response.success = True
        response.message = f'reset random monsters: removed={removed_count}, alive={alive_count}'
        return response

    def _handle_clear_nearest_obstacle(self, request, response):
        del request

        now = self.get_clock().now()
        if self._is_clear_on_cooldown(now):
            remaining = self.attack_cooldown - (
                (now - self.last_clear_stamp).nanoseconds * 1.0e-9
            )
            response.success = False
            response.message = f'cooldown active ({max(0.0, remaining):.2f}s remaining)'
            return response

        try:
            transform = self.tf_buffer.lookup_transform(
                self.scan_frame,
                self.obstacle_frame,
                Time(),
                timeout=Duration(seconds=0.10),
            )
        except Exception as exc:
            response.success = False
            response.message = f'waiting for TF {self.obstacle_frame} -> {self.scan_frame}: {exc}'
            return response

        candidate = self._find_nearest_clearable_obstacle(transform)
        if candidate is None:
            response.success = False
            response.message = (
                'no clearable virtual obstacle in front of the robot '
                f'(range <= {self.attack_range:.2f}m, '
                f'fov <= {math.degrees(self.attack_fov_rad):.1f}deg)'
            )
            return response

        index, obstacle, distance, angle = candidate
        obstacle.alive = False
        obstacle.target = None
        self.last_clear_stamp = now
        self.last_removed_stamp = now
        self._publish_delete_marker(index, now)
        if self.random_spawn_enabled and self.respawn_delay <= 0.0:
            self._maintain_random_obstacles(now)
        self._publish_monster_states(now)
        self.get_logger().info(
            f'Cleared virtual obstacle "{obstacle.name}" '
            f'at distance={distance:.2f}m, angle={math.degrees(angle):.1f}deg.'
        )

        response.success = True
        response.message = f'cleared {obstacle.name}'
        return response

    def _is_clear_on_cooldown(self, now: Time) -> bool:
        if self.last_clear_stamp is None or self.attack_cooldown <= 0.0:
            return False
        elapsed = (now - self.last_clear_stamp).nanoseconds * 1.0e-9
        return elapsed < self.attack_cooldown

    def _find_nearest_clearable_obstacle(self, transform):
        best = None
        half_fov = self.attack_fov_rad * 0.5

        for index, obstacle in enumerate(self.obstacles):
            if not obstacle.alive or not obstacle.clearable:
                continue

            x, y, _ = self._transform_point(
                obstacle.position[0],
                obstacle.position[1],
                0.0,
                transform,
            )
            distance = math.hypot(x, y)
            angle = math.atan2(y, x)

            if distance > self.attack_range:
                continue
            if abs(angle) > half_fov:
                continue

            if best is None or distance < best[2]:
                best = (index, obstacle, distance, angle)

        return best

    def _publish_delete_marker(self, obstacle_index: int, stamp: Time) -> None:
        marker_array = MarkerArray()
        # sub_id 0: body, 1: collision radius disk, 2: target line.
        for sub_id in range(3):
            marker = Marker()
            marker.header.stamp = stamp.to_msg()
            marker.header.frame_id = self.obstacle_frame
            marker.ns = 'virtual_dynamic_obstacles'
            marker.id = obstacle_index * 10 + sub_id
            marker.action = Marker.DELETE
            marker_array.markers.append(marker)
        self.marker_pub.publish(marker_array)

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
    node = VirtualDynamicObstacles()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
