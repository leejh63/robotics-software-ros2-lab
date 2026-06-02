#!/usr/bin/env python3

import json
import math
import os
from enum import Enum
from typing import Dict, List, Optional, Tuple

import rclpy
import tf2_ros
import yaml
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import Point, PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker, MarkerArray

try:
    from ament_index_python.packages import get_package_share_directory
except Exception:  # pragma: no cover - fallback for non-ROS static checks.
    get_package_share_directory = None


Point2 = Tuple[float, float]
Pose2 = Tuple[float, float, float]


class MissionState(str, Enum):
    INIT = 'INIT'
    PATROL_SEARCH = 'PATROL_SEARCH'
    MONSTER_DETECTED = 'MONSTER_DETECTED'
    APPROACH_MONSTER = 'APPROACH_MONSTER'
    ATTACK_MONSTER = 'ATTACK_MONSTER'
    CHECK_KILL_COUNT = 'CHECK_KILL_COUNT'
    GO_TO_EXIT = 'GO_TO_EXIT'
    ESCAPE_TO_EXIT = 'ESCAPE_TO_EXIT'  # Reserved. No transition uses this state yet.
    MISSION_DONE = 'MISSION_DONE'
    MISSION_FAILED = 'MISSION_FAILED'


def yaw_to_quaternion(yaw: float):
    qz = math.sin(yaw * 0.5)
    qw = math.cos(yaw * 0.5)
    return 0.0, 0.0, qz, qw


class MissionOccupancyMap:
    """Small ROS map_server YAML + PGM reader for map-grid patrol sampling."""

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

        self.image_path = str(data.get('image', '')).strip()
        if not self.image_path:
            raise ValueError(f'Map yaml has no image field: {self.map_yaml}')
        if not os.path.isabs(self.image_path):
            self.image_path = os.path.join(os.path.dirname(self.map_yaml), self.image_path)

        self.resolution = float(data.get('resolution', self.resolution))
        origin = data.get('origin', [0.0, 0.0, 0.0])
        if not isinstance(origin, list) or len(origin) < 3:
            raise ValueError(f'Map yaml origin must be [x, y, yaw]: {self.map_yaml}')
        self.origin = (float(origin[0]), float(origin[1]), float(origin[2]))
        self.negate = int(data.get('negate', 0))
        self.occupied_thresh = float(data.get('occupied_thresh', self.occupied_thresh))
        self.free_thresh = float(data.get('free_thresh', self.free_thresh))
        self._load_pgm()
        self.logger.info(
            f'Loaded mission patrol map: {self.map_yaml} '
            f'({self.width}x{self.height}, resolution={self.resolution:.3f}m)'
        )

    def _read_token(self, data: bytes, index: int) -> Tuple[str, int]:
        while index < len(data):
            value = data[index]
            if value in b' \t\r\n':
                index += 1
                continue
            if value == ord('#'):
                while index < len(data) and data[index] not in b'\r\n':
                    index += 1
                continue
            break
        start = index
        while index < len(data) and data[index] not in b' \t\r\n':
            index += 1
        return data[start:index].decode('ascii'), index

    def _load_pgm(self) -> None:
        with open(self.image_path, 'rb') as stream:
            data = stream.read()
        index = 0
        magic, index = self._read_token(data, index)
        width, index = self._read_token(data, index)
        height, index = self._read_token(data, index)
        max_value, index = self._read_token(data, index)
        self.width = int(width)
        self.height = int(height)
        max_value_int = int(max_value)
        if max_value_int <= 0 or max_value_int > 255:
            raise ValueError(f'Unsupported PGM max value {max_value_int}: {self.image_path}')

        if magic == 'P5':
            while index < len(data) and data[index] in b' \t\r\n':
                index += 1
            pixels = list(data[index:index + self.width * self.height])
        elif magic == 'P2':
            pixels = []
            for _ in range(self.width * self.height):
                token, index = self._read_token(data, index)
                pixels.append(int(token))
        else:
            raise ValueError(f'Unsupported PGM format {magic}: {self.image_path}')

        if len(pixels) != self.width * self.height:
            raise ValueError(f'PGM pixel count mismatch: {self.image_path}')
        self.pixels = pixels

    def world_to_map(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        mx = math.floor((x - self.origin[0]) / self.resolution)
        my_ros = math.floor((y - self.origin[1]) / self.resolution)
        if mx < 0 or my_ros < 0 or mx >= self.width or my_ros >= self.height:
            return None
        row = self.height - 1 - my_ros
        return int(mx), int(row)

    def is_free_cell(self, mx: int, row: int, unknown_is_blocked: bool = True) -> bool:
        if mx < 0 or row < 0 or mx >= self.width or row >= self.height:
            return False
        pixel = self.pixels[row * self.width + mx]
        if abs(pixel - 205) <= 1:
            return not unknown_is_blocked
        probability = (255 - pixel) / 255.0 if self.negate == 0 else pixel / 255.0
        return probability <= self.free_thresh

    def is_clear_world(self, x: float, y: float, clearance: float, unknown_is_blocked: bool = True) -> bool:
        center = self.world_to_map(x, y)
        if center is None:
            return False
        mx, row = center
        if not self.is_free_cell(mx, row, unknown_is_blocked):
            return False
        if clearance <= 0.0:
            return True

        radius_cells = max(1, int(math.ceil(clearance / self.resolution)))
        for dy in range(-radius_cells, radius_cells + 1):
            for dx in range(-radius_cells, radius_cells + 1):
                if math.hypot(dx * self.resolution, dy * self.resolution) > clearance:
                    continue
                if not self.is_free_cell(mx + dx, row + dy, unknown_is_blocked):
                    return False
        return True

    def generate_grid_waypoints(
        self,
        spacing: float,
        clearance: float,
        max_waypoints: int,
        unknown_is_blocked: bool = True,
    ) -> List[Pose2]:
        spacing = max(self.resolution, float(spacing))
        min_x = self.origin[0] + clearance
        max_x = self.origin[0] + self.width * self.resolution - clearance
        min_y = self.origin[1] + clearance
        max_y = self.origin[1] + self.height * self.resolution - clearance

        rows: List[List[Point2]] = []
        y = min_y
        while y <= max_y + 1.0e-9:
            row_points: List[Point2] = []
            x = min_x
            while x <= max_x + 1.0e-9:
                if self.is_clear_world(x, y, clearance, unknown_is_blocked):
                    row_points.append((x, y))
                x += spacing
            if row_points:
                if len(rows) % 2 == 1:
                    row_points.reverse()
                rows.append(row_points)
            y += spacing

        points = [point for row in rows for point in row]
        if max_waypoints > 0 and len(points) > max_waypoints:
            if max_waypoints == 1:
                points = [points[0]]
            else:
                indices = [round(i * (len(points) - 1) / float(max_waypoints - 1)) for i in range(max_waypoints)]
                points = [points[index] for index in indices]

        poses: List[Pose2] = []
        for index, point in enumerate(points):
            if len(points) > 1:
                nxt = points[(index + 1) % len(points)]
                yaw = math.atan2(nxt[1] - point[1], nxt[0] - point[0])
            else:
                yaw = 0.0
            poses.append((point[0], point[1], yaw))
        return poses


class MonsterMissionNode(Node):
    """Stage 4 mission manager.

    Detector candidates interrupt map-wide patrol goals, then the robot approaches,
    clears monsters, and moves to the configured exit pose after the kill target.
    """

    def __init__(self):
        super().__init__('monster_mission_node')

        self.declare_parameter('candidate_topic', '/lee/detected_monster_candidates')
        self.declare_parameter('mission_status_topic', '/lee/monster_mission_status')
        self.declare_parameter('patrol_marker_topic', '/lee/patrol_waypoint_markers')
        self.declare_parameter('clear_service_name', '/lee/clear_nearest_virtual_obstacle')
        self.declare_parameter('navigate_action_name', '/lee/navigate_to_pose')
        self.declare_parameter('map_frame', 'map_lee')
        self.declare_parameter('robot_frame', 'base_scan')
        self.declare_parameter('target_kill_count', 3)
        self.declare_parameter('update_rate', 2.0)
        self.declare_parameter('autostart', True)
        self.declare_parameter('approach_distance', 0.75)
        self.declare_parameter('clear_distance', 0.90)
        self.declare_parameter('candidate_center_offset', 0.25)
        self.declare_parameter('candidate_freshness_sec', 2.0)
        self.declare_parameter('max_candidate_distance', 1.60)
        self.declare_parameter('max_clear_attempts', 4)
        self.declare_parameter('clear_retry_delay_sec', 0.4)
        self.declare_parameter('patrol_mode', 'map_grid')
        self.declare_parameter('map_yaml', 'maps/slam_map.yaml')
        self.declare_parameter('patrol_grid_spacing', 0.80)
        self.declare_parameter('patrol_wall_clearance', 0.28)
        self.declare_parameter('patrol_max_waypoints', 80)
        self.declare_parameter('patrol_start_nearest', True)
        self.declare_parameter('patrol_unknown_is_blocked', True)
        self.declare_parameter('search_waypoints', '0.0,0.0,0.0;0.8,0.0,0.0;0.8,0.8,0.0;0.0,0.8,0.0')
        self.declare_parameter('exit_pose', '0.0,0.0,0.0')
        self.declare_parameter('escape_state_reserved', True)

        self.candidate_topic = str(self.get_parameter('candidate_topic').value)
        self.mission_status_topic = str(self.get_parameter('mission_status_topic').value)
        self.patrol_marker_topic = str(self.get_parameter('patrol_marker_topic').value)
        self.clear_service_name = str(self.get_parameter('clear_service_name').value)
        self.navigate_action_name = str(self.get_parameter('navigate_action_name').value)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.target_kill_count = int(self.get_parameter('target_kill_count').value)
        self.update_rate = max(0.2, float(self.get_parameter('update_rate').value))
        self.enabled = bool(self.get_parameter('autostart').value)
        self.approach_distance = float(self.get_parameter('approach_distance').value)
        self.clear_distance = float(self.get_parameter('clear_distance').value)
        self.candidate_center_offset = max(0.0, float(self.get_parameter('candidate_center_offset').value))
        self.candidate_freshness_sec = float(self.get_parameter('candidate_freshness_sec').value)
        self.max_candidate_distance = float(self.get_parameter('max_candidate_distance').value)
        self.max_clear_attempts = max(1, int(self.get_parameter('max_clear_attempts').value))
        self.clear_retry_delay_sec = max(0.0, float(self.get_parameter('clear_retry_delay_sec').value))
        self.patrol_mode = str(self.get_parameter('patrol_mode').value).strip().lower()
        self.map_yaml = self._resolve_path(str(self.get_parameter('map_yaml').value))
        self.patrol_grid_spacing = max(0.20, float(self.get_parameter('patrol_grid_spacing').value))
        self.patrol_wall_clearance = max(0.0, float(self.get_parameter('patrol_wall_clearance').value))
        self.patrol_max_waypoints = max(0, int(self.get_parameter('patrol_max_waypoints').value))
        self.patrol_start_nearest = bool(self.get_parameter('patrol_start_nearest').value)
        self.patrol_unknown_is_blocked = bool(self.get_parameter('patrol_unknown_is_blocked').value)
        self.manual_search_waypoints = self._parse_pose_list(str(self.get_parameter('search_waypoints').value))
        self.exit_pose = self._parse_pose(str(self.get_parameter('exit_pose').value))
        self.escape_state_reserved = bool(self.get_parameter('escape_state_reserved').value)

        self.search_waypoints = self._load_patrol_waypoints()
        if not self.search_waypoints:
            self.search_waypoints = self.manual_search_waypoints or [(0.0, 0.0, 0.0)]

        self.state = MissionState.INIT
        self.kill_count = 0
        self.current_waypoint_index = 0
        self.patrol_start_aligned = False
        self.latest_candidates: List[Dict] = []
        self.latest_candidate_stamp: Optional[Time] = None
        self.current_target: Optional[Dict] = None
        self.current_goal_kind: Optional[str] = None
        self.current_goal_handle = None
        self.goal_active = False
        self.cancel_active = False
        self.cancel_after_accept = False
        self.clear_active = False
        self.clear_attempt_count = 0
        self.next_clear_time: Optional[Time] = None
        self.done = False
        self.last_wait_log_time: Optional[Time] = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.nav_client = ActionClient(self, NavigateToPose, self.navigate_action_name)
        self.clear_client = self.create_client(Trigger, self.clear_service_name)
        self.candidate_sub = self.create_subscription(String, self.candidate_topic, self._on_candidates, 10)
        self.status_pub = self.create_publisher(String, self.mission_status_topic, 10)
        self.patrol_marker_pub = self.create_publisher(MarkerArray, self.patrol_marker_topic, 10)
        self.timer = self.create_timer(1.0 / self.update_rate, self._on_timer)
        self.marker_timer = self.create_timer(2.0, self._publish_patrol_markers)

        self.get_logger().info(
            'Monster mission ready: '
            f'candidate_topic={self.candidate_topic}, target_kill_count={self.target_kill_count}, '
            f'max_candidate_distance={self.max_candidate_distance:.2f}m, '
            f'approach_distance={self.approach_distance:.2f}m, clear_distance={self.clear_distance:.2f}m, '
            f'candidate_center_offset={self.candidate_center_offset:.2f}m, '
            f'max_clear_attempts={self.max_clear_attempts}, '
            f'patrol_mode={self.patrol_mode}, waypoints={len(self.search_waypoints)}, '
            f'exit_pose={self.exit_pose}, escape_state_reserved={self.escape_state_reserved}'
        )

    def _resolve_path(self, path: str) -> str:
        path = os.path.expanduser(path.strip())
        if os.path.isabs(path):
            return path
        candidates = []
        if get_package_share_directory is not None:
            try:
                candidates.append(os.path.join(get_package_share_directory('lee_robot_description'), path))
            except Exception:
                pass
        candidates.append(os.path.join(os.getcwd(), path))
        for candidate in candidates:
            if os.path.exists(candidate):
                return candidate
        return candidates[0] if candidates else path

    def _load_patrol_waypoints(self) -> List[Pose2]:
        if self.patrol_mode in ('manual', 'waypoints', 'static'):
            return list(self.manual_search_waypoints)
        if self.patrol_mode not in ('map_grid', 'grid', 'coverage'):
            self.get_logger().warn(
                f'Unknown patrol_mode={self.patrol_mode}; falling back to manual search_waypoints.'
            )
            return list(self.manual_search_waypoints)

        try:
            occupancy_map = MissionOccupancyMap(self.map_yaml, self.get_logger())
            waypoints = occupancy_map.generate_grid_waypoints(
                spacing=self.patrol_grid_spacing,
                clearance=self.patrol_wall_clearance,
                max_waypoints=self.patrol_max_waypoints,
                unknown_is_blocked=self.patrol_unknown_is_blocked,
            )
        except Exception as exc:
            self.get_logger().warn(f'Failed to generate map-grid patrol waypoints: {exc}')
            return list(self.manual_search_waypoints)

        if not waypoints:
            self.get_logger().warn('Map-grid patrol generated no waypoints; falling back to manual search_waypoints.')
            return list(self.manual_search_waypoints)

        self.get_logger().info(
            f'Generated {len(waypoints)} map-grid patrol waypoints '
            f'(spacing={self.patrol_grid_spacing:.2f}m, clearance={self.patrol_wall_clearance:.2f}m).'
        )
        return waypoints

    def _on_candidates(self, message: String) -> None:
        try:
            payload = json.loads(message.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f'Ignored invalid candidate JSON: {exc}')
            return
        if not isinstance(payload, dict):
            return
        candidates = payload.get('candidates', [])
        if not isinstance(candidates, list):
            return
        self.latest_candidates = [candidate for candidate in candidates if isinstance(candidate, dict)]
        self.latest_candidate_stamp = self.get_clock().now()

    def _on_timer(self) -> None:
        self._publish_status()
        if not self.enabled or self.done:
            return

        if self.clear_active:
            return

        if self.goal_active:
            self._maybe_interrupt_patrol_for_candidate()
            return

        if self.cancel_active:
            return

        if self.state == MissionState.INIT:
            self._transition(MissionState.PATROL_SEARCH, 'mission started')
            return

        if self.state == MissionState.CHECK_KILL_COUNT:
            if self.kill_count >= self.target_kill_count:
                self._transition(MissionState.GO_TO_EXIT, 'target kill count reached')
            else:
                self._transition(MissionState.PATROL_SEARCH, 'target kill count not reached')
            return

        if self.state == MissionState.PATROL_SEARCH:
            candidate = self._select_candidate()
            if candidate is not None:
                self.current_target = candidate
                self._transition(MissionState.MONSTER_DETECTED, 'detector candidate selected')
                return
            self._send_next_patrol_goal()
            return

        if self.state == MissionState.MONSTER_DETECTED:
            self._transition(MissionState.APPROACH_MONSTER, 'approaching detected candidate')
            return

        if self.state == MissionState.APPROACH_MONSTER:
            self._approach_current_target()
            return

        if self.state == MissionState.ATTACK_MONSTER:
            if self.next_clear_time is not None:
                wait_sec = (self.next_clear_time - self.get_clock().now()).nanoseconds * 1.0e-9
                if wait_sec > 0.0:
                    self._log_waiting(f'waiting {wait_sec:.1f}s before retrying clear service')
                    return
                self.next_clear_time = None
            self._call_clear_service()
            return

        if self.state == MissionState.GO_TO_EXIT:
            self._send_exit_goal()
            return

        if self.state == MissionState.ESCAPE_TO_EXIT:
            self.get_logger().warn('ESCAPE_TO_EXIT is reserved but not implemented yet.')
            self._transition(MissionState.MISSION_FAILED, 'escape behavior not implemented')
            return

    def _maybe_interrupt_patrol_for_candidate(self) -> None:
        if self.current_goal_kind != 'patrol':
            return
        if self.cancel_active or self.cancel_after_accept:
            return

        candidate = self._select_candidate()
        if candidate is None:
            return

        self.current_target = candidate
        self._request_current_goal_cancel('detector candidate selected during patrol')

    def _select_candidate(self) -> Optional[Dict]:
        if not self.latest_candidates or self.latest_candidate_stamp is None:
            return None
        age = (self.get_clock().now() - self.latest_candidate_stamp).nanoseconds * 1.0e-9
        if age > self.candidate_freshness_sec:
            return None

        robot_position = self._lookup_robot_position()
        if robot_position is None:
            self._log_waiting(f'waiting for TF {self.map_frame} -> {self.robot_frame}')
            return None

        best = None
        best_distance = float('inf')
        for candidate in self.latest_candidates:
            try:
                position = (float(candidate['x']), float(candidate['y']))
            except (KeyError, TypeError, ValueError):
                continue
            distance = self._distance(robot_position, position)
            if distance > self.max_candidate_distance:
                continue
            if distance < best_distance:
                best = candidate
                best_distance = distance
        return best

    def _send_next_patrol_goal(self) -> None:
        if not self.search_waypoints:
            self._log_waiting('no search waypoints configured')
            return
        self._align_patrol_start_to_robot_once()
        pose = self.search_waypoints[self.current_waypoint_index % len(self.search_waypoints)]
        self._send_navigation_goal(self._make_pose(pose), 'patrol')

    def _align_patrol_start_to_robot_once(self) -> None:
        if self.patrol_start_aligned or not self.patrol_start_nearest or not self.search_waypoints:
            self.patrol_start_aligned = True
            return
        robot_position = self._lookup_robot_position()
        if robot_position is None:
            return
        best_index = 0
        best_distance = float('inf')
        for index, waypoint in enumerate(self.search_waypoints):
            distance = self._distance(robot_position, (waypoint[0], waypoint[1]))
            if distance < best_distance:
                best_index = index
                best_distance = distance
        self.current_waypoint_index = best_index
        self.patrol_start_aligned = True
        self.get_logger().info(
            f'Patrol start aligned to nearest waypoint index={best_index}, distance={best_distance:.2f}m.'
        )

    def _approach_current_target(self) -> None:
        if self.current_target is None:
            self._transition(MissionState.PATROL_SEARCH, 'no current target')
            return

        robot_position = self._lookup_robot_position()
        if robot_position is None:
            self._log_waiting(f'waiting for TF {self.map_frame} -> {self.robot_frame}')
            return

        target_position = self._candidate_target_position(self.current_target, robot_position)
        if target_position is None:
            self._transition(MissionState.PATROL_SEARCH, 'invalid target candidate')
            return

        if self._distance(robot_position, target_position) <= self.clear_distance:
            self._transition(MissionState.ATTACK_MONSTER, 'target is within clear distance')
            return

        approach_pose = self._make_approach_pose(robot_position, target_position)
        self._send_navigation_goal(approach_pose, 'hunt')

    def _send_exit_goal(self) -> None:
        self._send_navigation_goal(self._make_pose(self.exit_pose), 'exit')

    def _send_navigation_goal(self, pose: PoseStamped, kind: str) -> None:
        if self.goal_active or self.cancel_active:
            return
        if not self.nav_client.wait_for_server(timeout_sec=0.1):
            self._log_waiting(f'waiting for Nav2 action {self.navigate_action_name}')
            return

        goal = NavigateToPose.Goal()
        goal.pose = pose
        self.goal_active = True
        self.cancel_active = False
        self.cancel_after_accept = False
        self.current_goal_handle = None
        self.current_goal_kind = kind
        self.get_logger().info(
            f'Sending {kind} goal: ({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})'
        )
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.goal_active = False
            self.cancel_active = False
            self.cancel_after_accept = False
            self.current_goal_handle = None
            self.get_logger().warn(f'Failed to send Nav2 goal: {exc}')
            self._handle_navigation_failed(self.current_goal_kind)
            return

        if not goal_handle.accepted:
            self.goal_active = False
            self.cancel_active = False
            self.cancel_after_accept = False
            self.current_goal_handle = None
            self.get_logger().warn('Nav2 goal was rejected.')
            self._handle_navigation_failed(self.current_goal_kind)
            return

        self.current_goal_handle = goal_handle
        if self.cancel_after_accept:
            self.cancel_active = False
            self.cancel_after_accept = False
            self._request_current_goal_cancel('queued patrol cancel after goal acceptance')

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_navigation_result)

    def _request_current_goal_cancel(self, reason: str) -> None:
        if not self.goal_active:
            return
        if self.cancel_active or self.cancel_after_accept:
            return

        self.cancel_active = True
        self.get_logger().info(f'Requesting Nav2 {self.current_goal_kind} goal cancel: {reason}')
        if self.current_goal_handle is None:
            self.cancel_after_accept = True
            return

        self.cancel_after_accept = False
        future = self.current_goal_handle.cancel_goal_async()
        future.add_done_callback(self._on_goal_cancel_response)

    def _on_goal_cancel_response(self, future) -> None:
        try:
            response = future.result()
        except Exception as exc:
            self.cancel_active = False
            self.cancel_after_accept = False
            self.get_logger().warn(f'Failed to cancel Nav2 goal: {exc}')
            return

        goals_canceling = getattr(response, 'goals_canceling', [])
        if goals_canceling:
            self.get_logger().info('Nav2 goal cancel accepted; waiting for canceled result.')
            return

        self.cancel_active = False
        self.cancel_after_accept = False
        self.get_logger().warn('Nav2 goal cancel was not accepted.')

    def _on_navigation_result(self, future) -> None:
        self.goal_active = False
        was_canceling = self.cancel_active or self.cancel_after_accept
        self.cancel_active = False
        self.cancel_after_accept = False
        self.current_goal_handle = None
        kind = self.current_goal_kind
        self.current_goal_kind = None
        try:
            result = future.result()
        except Exception as exc:
            self.get_logger().warn(f'Nav2 result failed: {exc}')
            self._handle_navigation_failed(kind)
            return

        status = getattr(result, 'status', None)
        if status != GoalStatus.STATUS_SUCCEEDED:
            if status == GoalStatus.STATUS_CANCELED and kind == 'patrol' and self.current_target is not None:
                self.get_logger().info('Patrol goal canceled; switching to detected monster.')
                self._transition(MissionState.MONSTER_DETECTED, 'patrol canceled for detector candidate')
                return
            if status == GoalStatus.STATUS_CANCELED and was_canceling:
                self.get_logger().info(f'Nav2 {kind} goal canceled.')
                self._transition(MissionState.PATROL_SEARCH, 'navigation goal canceled')
                return
            self.get_logger().warn(f'Nav2 {kind} goal finished with status={status}.')
            self._handle_navigation_failed(kind)
            return

        if kind == 'patrol':
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.search_waypoints)
            self._transition(MissionState.PATROL_SEARCH, 'patrol waypoint reached')
        elif kind == 'hunt':
            self._transition(MissionState.ATTACK_MONSTER, 'hunt approach goal reached')
        elif kind == 'exit':
            self.done = True
            self._transition(MissionState.MISSION_DONE, 'exit pose reached')
        else:
            self._transition(MissionState.PATROL_SEARCH, 'unknown goal kind completed')

    def _handle_navigation_failed(self, kind: Optional[str] = None) -> None:
        if kind == 'exit':
            self.done = True
            self._transition(MissionState.MISSION_FAILED, 'exit navigation failed')
            return
        if kind == 'hunt':
            self.current_target = None
            self._transition(MissionState.PATROL_SEARCH, 'hunt navigation failed; returning to patrol')
            return
        if kind == 'patrol' and self.search_waypoints:
            self.current_waypoint_index = (self.current_waypoint_index + 1) % len(self.search_waypoints)
            self._transition(MissionState.PATROL_SEARCH, 'patrol navigation failed; skipping waypoint')
            return
        self._transition(MissionState.PATROL_SEARCH, 'navigation failed; continuing patrol')

    def _call_clear_service(self) -> None:
        if not self.clear_client.wait_for_service(timeout_sec=0.1):
            self._log_waiting(f'waiting for clear service {self.clear_service_name}')
            return
        self.clear_active = True
        self.clear_attempt_count += 1
        self.get_logger().info(
            f'Calling clear service attempt {self.clear_attempt_count}/{self.max_clear_attempts}'
        )
        future = self.clear_client.call_async(Trigger.Request())
        future.add_done_callback(self._on_clear_result)

    def _on_clear_result(self, future) -> None:
        self.clear_active = False
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().warn(f'Clear service call failed: {exc}')
            self.current_target = None
            self._transition(MissionState.PATROL_SEARCH, 'clear service exception')
            return

        if response.success:
            self.clear_attempt_count = 0
            self.next_clear_time = None
            self.kill_count += 1
            self.get_logger().info(
                f'Clear success: {response.message}; kill_count={self.kill_count}/{self.target_kill_count}'
            )
            self.current_target = None
            self._transition(MissionState.CHECK_KILL_COUNT, 'clear succeeded')
            return

        self.get_logger().warn(f'Clear failed: {response.message}')
        if self.clear_attempt_count < self.max_clear_attempts:
            self.next_clear_time = self.get_clock().now() + Duration(seconds=self.clear_retry_delay_sec)
            self._transition(MissionState.ATTACK_MONSTER, 'clear failed; retrying')
            return

        self.clear_attempt_count = 0
        self.next_clear_time = None
        self.current_target = None
        self._transition(MissionState.PATROL_SEARCH, 'clear failed too many times; returning to patrol')

    def _candidate_target_position(self, candidate: Dict, robot_position: Point2) -> Optional[Point2]:
        try:
            surface_position = (float(candidate['x']), float(candidate['y']))
        except (KeyError, TypeError, ValueError):
            return None

        dx = surface_position[0] - robot_position[0]
        dy = surface_position[1] - robot_position[1]
        distance = math.hypot(dx, dy)
        if distance <= 1.0e-6 or self.candidate_center_offset <= 0.0:
            return surface_position

        ux, uy = dx / distance, dy / distance
        return (
            surface_position[0] + ux * self.candidate_center_offset,
            surface_position[1] + uy * self.candidate_center_offset,
        )

    def _lookup_robot_position(self) -> Optional[Point2]:
        try:
            transform = self.tf_buffer.lookup_transform(
                self.map_frame,
                self.robot_frame,
                Time(),
                timeout=Duration(seconds=0.05),
            )
        except Exception:
            return None
        return (
            float(transform.transform.translation.x),
            float(transform.transform.translation.y),
        )

    def _make_approach_pose(self, robot_position: Point2, target_position: Point2) -> PoseStamped:
        dx = target_position[0] - robot_position[0]
        dy = target_position[1] - robot_position[1]
        distance = math.hypot(dx, dy)
        if distance <= 1.0e-6:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = dx / distance, dy / distance
        goal_x = target_position[0] - ux * self.approach_distance
        goal_y = target_position[1] - uy * self.approach_distance
        yaw = math.atan2(target_position[1] - goal_y, target_position[0] - goal_x)
        return self._make_pose((goal_x, goal_y, yaw))

    def _make_pose(self, pose: Pose2) -> PoseStamped:
        x, y, yaw = pose
        qx, qy, qz, qw = yaw_to_quaternion(yaw)
        message = PoseStamped()
        message.header.frame_id = self.map_frame
        message.header.stamp = self.get_clock().now().to_msg()
        message.pose.position.x = float(x)
        message.pose.position.y = float(y)
        message.pose.position.z = 0.0
        message.pose.orientation.x = qx
        message.pose.orientation.y = qy
        message.pose.orientation.z = qz
        message.pose.orientation.w = qw
        return message

    def _parse_pose_list(self, text: str) -> List[Pose2]:
        poses = []
        for chunk in text.split(';'):
            chunk = chunk.strip()
            if not chunk:
                continue
            poses.append(self._parse_pose(chunk))
        return poses

    def _parse_pose(self, text: str) -> Pose2:
        values = [float(value.strip()) for value in text.split(',') if value.strip()]
        if len(values) < 2:
            raise ValueError(f'Pose must be "x,y" or "x,y,yaw": {text}')
        yaw = values[2] if len(values) >= 3 else 0.0
        return float(values[0]), float(values[1]), float(yaw)

    def _transition(self, next_state: MissionState, reason: str) -> None:
        if self.state == next_state:
            return
        if next_state == MissionState.ATTACK_MONSTER:
            self.clear_attempt_count = 0
            self.next_clear_time = None
        if self.state == MissionState.ATTACK_MONSTER and next_state != MissionState.ATTACK_MONSTER:
            self.next_clear_time = None
        self.get_logger().info(f'Mission state: {self.state.value} -> {next_state.value} ({reason})')
        self.state = next_state
        self._publish_status()

    def _publish_patrol_markers(self) -> None:
        if not self.search_waypoints:
            return

        now = self.get_clock().now().to_msg()
        array = MarkerArray()

        points_marker = Marker()
        points_marker.header.frame_id = self.map_frame
        points_marker.header.stamp = now
        points_marker.ns = 'patrol_waypoints'
        points_marker.id = 0
        points_marker.type = Marker.SPHERE_LIST
        points_marker.action = Marker.ADD
        points_marker.pose.orientation.w = 1.0
        points_marker.scale.x = 0.08
        points_marker.scale.y = 0.08
        points_marker.scale.z = 0.08
        points_marker.color.r = 0.1
        points_marker.color.g = 0.8
        points_marker.color.b = 1.0
        points_marker.color.a = 0.9

        path_marker = Marker()
        path_marker.header.frame_id = self.map_frame
        path_marker.header.stamp = now
        path_marker.ns = 'patrol_waypoints'
        path_marker.id = 1
        path_marker.type = Marker.LINE_STRIP
        path_marker.action = Marker.ADD
        path_marker.pose.orientation.w = 1.0
        path_marker.scale.x = 0.025
        path_marker.color.r = 0.1
        path_marker.color.g = 0.8
        path_marker.color.b = 1.0
        path_marker.color.a = 0.45

        for pose in self.search_waypoints:
            point = Point()
            point.x = float(pose[0])
            point.y = float(pose[1])
            point.z = 0.02
            points_marker.points.append(point)
            path_marker.points.append(point)
        if len(path_marker.points) > 1:
            first = Point()
            first.x = path_marker.points[0].x
            first.y = path_marker.points[0].y
            first.z = path_marker.points[0].z
            path_marker.points.append(first)

        current_marker = Marker()
        current_marker.header.frame_id = self.map_frame
        current_marker.header.stamp = now
        current_marker.ns = 'patrol_waypoints'
        current_marker.id = 2
        current_marker.type = Marker.SPHERE
        current_marker.action = Marker.ADD
        current_marker.pose.orientation.w = 1.0
        current = self.search_waypoints[self.current_waypoint_index % len(self.search_waypoints)]
        current_marker.pose.position.x = float(current[0])
        current_marker.pose.position.y = float(current[1])
        current_marker.pose.position.z = 0.06
        current_marker.scale.x = 0.16
        current_marker.scale.y = 0.16
        current_marker.scale.z = 0.16
        current_marker.color.r = 1.0
        current_marker.color.g = 0.9
        current_marker.color.b = 0.1
        current_marker.color.a = 1.0

        array.markers.extend([points_marker, path_marker, current_marker])
        self.patrol_marker_pub.publish(array)

    def _publish_status(self) -> None:
        now = self.get_clock().now()
        payload = {
            'stamp': {
                'sec': int(now.nanoseconds // 1_000_000_000),
                'nanosec': int(now.nanoseconds % 1_000_000_000),
            },
            'state': self.state.value,
            'kill_count': int(self.kill_count),
            'target_kill_count': int(self.target_kill_count),
            'patrol_mode': self.patrol_mode,
            'patrol_waypoint_count': int(len(self.search_waypoints)),
            'current_waypoint_index': int(self.current_waypoint_index),
            'goal_active': bool(self.goal_active),
            'current_goal_kind': self.current_goal_kind,
            'cancel_active': bool(self.cancel_active or self.cancel_after_accept),
            'clear_active': bool(self.clear_active),
            'clear_attempt_count': int(self.clear_attempt_count),
            'max_clear_attempts': int(self.max_clear_attempts),
            'latest_candidate_count': int(len(self.latest_candidates)),
            'current_target': self.current_target,
            'done': bool(self.done),
        }
        self.status_pub.publish(String(data=json.dumps(payload, separators=(',', ':'))))

    def _log_waiting(self, message: str) -> None:
        now = self.get_clock().now()
        if self.last_wait_log_time is not None:
            dt = (now - self.last_wait_log_time).nanoseconds * 1.0e-9
            if dt < 3.0:
                return
        self.last_wait_log_time = now
        self.get_logger().info(message)

    def _distance(self, first: Point2, second: Point2) -> float:
        return math.hypot(first[0] - second[0], first[1] - second[1])


def main(args=None):
    rclpy.init(args=args)
    node = MonsterMissionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
