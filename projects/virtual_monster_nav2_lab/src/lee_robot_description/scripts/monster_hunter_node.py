#!/usr/bin/env python3

import json
import math
from typing import Dict, List, Optional, Tuple

import rclpy
import tf2_ros
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node
from rclpy.time import Time
from std_msgs.msg import String
from std_srvs.srv import Trigger


Point2 = Tuple[float, float]


def yaw_to_quaternion(yaw: float):
    qz = math.sin(yaw * 0.5)
    qw = math.cos(yaw * 0.5)
    return 0.0, 0.0, qz, qw


class MonsterHunterNode(Node):
    """Minimal Stage 3 hunter.

    This node does one thing first: select an alive virtual monster from the
    /virtual_monster_states JSON topic, navigate near it, and call the existing
    clear service. Mission/exploration behavior is intentionally left for later
    stages.
    """

    def __init__(self):
        super().__init__('monster_hunter_node')

        self.declare_parameter('state_topic', '/lee/virtual_monster_states')
        self.declare_parameter('clear_service_name', '/lee/clear_nearest_virtual_obstacle')
        self.declare_parameter('navigate_action_name', '/lee/navigate_to_pose')
        self.declare_parameter('map_frame', 'map_lee')
        self.declare_parameter('robot_frame', 'base_scan')
        self.declare_parameter('approach_distance', 0.65)
        self.declare_parameter('clear_distance', 0.75)
        self.declare_parameter('target_kill_count', 1)
        self.declare_parameter('update_rate', 2.0)
        self.declare_parameter('autostart', True)

        self.state_topic = str(self.get_parameter('state_topic').value)
        self.clear_service_name = str(self.get_parameter('clear_service_name').value)
        self.navigate_action_name = str(self.get_parameter('navigate_action_name').value)
        self.map_frame = str(self.get_parameter('map_frame').value)
        self.robot_frame = str(self.get_parameter('robot_frame').value)
        self.approach_distance = float(self.get_parameter('approach_distance').value)
        self.clear_distance = float(self.get_parameter('clear_distance').value)
        self.target_kill_count = int(self.get_parameter('target_kill_count').value)
        self.update_rate = max(0.2, float(self.get_parameter('update_rate').value))
        self.enabled = bool(self.get_parameter('autostart').value)

        self.latest_state: Optional[Dict] = None
        self.current_target_key: Optional[str] = None
        self.goal_active = False
        self.clear_active = False
        self.kill_count = 0
        self.done = False
        self.last_wait_log_time: Optional[Time] = None

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.state_sub = self.create_subscription(
            String,
            self.state_topic,
            self._on_state,
            10,
        )
        self.clear_client = self.create_client(Trigger, self.clear_service_name)
        self.nav_client = ActionClient(self, NavigateToPose, self.navigate_action_name)
        self.timer = self.create_timer(1.0 / self.update_rate, self._on_timer)

        self.get_logger().info(
            'Monster hunter ready: '
            f'state_topic={self.state_topic}, '
            f'clear_service={self.clear_service_name}, '
            f'navigate_action={self.navigate_action_name}, '
            f'target_kill_count={self.target_kill_count}'
        )

    def _on_state(self, message: String) -> None:
        try:
            state = json.loads(message.data)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f'Ignored invalid monster state JSON: {exc}')
            return
        if not isinstance(state, dict):
            self.get_logger().warn('Ignored monster state because JSON root is not an object.')
            return
        self.latest_state = state

    def _on_timer(self) -> None:
        if not self.enabled or self.done:
            return
        if self.kill_count >= self.target_kill_count:
            self.done = True
            self.get_logger().info(f'Monster hunter done: kill_count={self.kill_count}')
            return
        if self.goal_active or self.clear_active:
            return
        if self.latest_state is None:
            self._log_waiting('waiting for monster state topic')
            return

        robot_position = self._lookup_robot_position()
        if robot_position is None:
            self._log_waiting(f'waiting for TF {self.map_frame} -> {self.robot_frame}')
            return

        target = self._select_nearest_monster(robot_position)
        if target is None:
            self._log_waiting('waiting for an alive monster')
            return

        self.current_target_key = self._monster_key(target)
        monster_position = (float(target['x']), float(target['y']))
        distance = self._distance(robot_position, monster_position)
        if distance <= self.clear_distance:
            self._call_clear_service()
            return

        goal_pose = self._make_approach_pose(robot_position, monster_position)
        self._send_navigation_goal(goal_pose, target)

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

    def _select_nearest_monster(self, robot_position: Point2) -> Optional[Dict]:
        monsters = self.latest_state.get('monsters', []) if self.latest_state else []
        if not isinstance(monsters, list):
            return None

        best = None
        best_distance = float('inf')
        for monster in monsters:
            if not isinstance(monster, dict):
                continue
            if not monster.get('alive', False):
                continue
            if not monster.get('clearable', True):
                continue
            try:
                position = (float(monster['x']), float(monster['y']))
            except (KeyError, TypeError, ValueError):
                continue
            distance = self._distance(robot_position, position)
            if distance < best_distance:
                best = monster
                best_distance = distance
        return best

    def _make_approach_pose(self, robot_position: Point2, monster_position: Point2) -> PoseStamped:
        dx = monster_position[0] - robot_position[0]
        dy = monster_position[1] - robot_position[1]
        distance = math.hypot(dx, dy)
        if distance <= 1.0e-6:
            ux, uy = 1.0, 0.0
        else:
            ux, uy = dx / distance, dy / distance

        goal_x = monster_position[0] - ux * self.approach_distance
        goal_y = monster_position[1] - uy * self.approach_distance
        yaw = math.atan2(monster_position[1] - goal_y, monster_position[0] - goal_x)
        qx, qy, qz, qw = yaw_to_quaternion(yaw)

        pose = PoseStamped()
        pose.header.frame_id = self.map_frame
        pose.header.stamp = self.get_clock().now().to_msg()
        pose.pose.position.x = goal_x
        pose.pose.position.y = goal_y
        pose.pose.position.z = 0.0
        pose.pose.orientation.x = qx
        pose.pose.orientation.y = qy
        pose.pose.orientation.z = qz
        pose.pose.orientation.w = qw
        return pose

    def _send_navigation_goal(self, pose: PoseStamped, target: Dict) -> None:
        if not self.nav_client.wait_for_server(timeout_sec=0.1):
            self._log_waiting(f'waiting for Nav2 action {self.navigate_action_name}')
            return

        goal = NavigateToPose.Goal()
        goal.pose = pose
        self.goal_active = True
        self.get_logger().info(
            f'Navigate to monster {target.get("name", target.get("id", "unknown"))}: '
            f'goal=({pose.pose.position.x:.2f}, {pose.pose.position.y:.2f})'
        )
        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self._on_goal_response)

    def _on_goal_response(self, future) -> None:
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.goal_active = False
            self.get_logger().warn(f'Failed to send Nav2 goal: {exc}')
            return

        if not goal_handle.accepted:
            self.goal_active = False
            self.get_logger().warn('Nav2 goal was rejected.')
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_navigation_result)

    def _on_navigation_result(self, future) -> None:
        self.goal_active = False
        try:
            result = future.result()
        except Exception as exc:
            self.get_logger().warn(f'Nav2 result failed: {exc}')
            return

        # In NavigateToPose, a completed result callback means Nav2 finished the goal.
        # For this Stage 3 node, try the clear service and let the service decide
        # whether the robot is close enough and facing the monster.
        self.get_logger().info(f'Nav2 finished with status={getattr(result, "status", "unknown")}; trying clear service.')
        self._call_clear_service()

    def _call_clear_service(self) -> None:
        if not self.clear_client.wait_for_service(timeout_sec=0.1):
            self._log_waiting(f'waiting for clear service {self.clear_service_name}')
            return
        self.clear_active = True
        future = self.clear_client.call_async(Trigger.Request())
        future.add_done_callback(self._on_clear_result)

    def _on_clear_result(self, future) -> None:
        self.clear_active = False
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().warn(f'Clear service call failed: {exc}')
            return

        if response.success:
            self.kill_count += 1
            self.get_logger().info(
                f'Clear success: {response.message}; kill_count={self.kill_count}/{self.target_kill_count}'
            )
            self.current_target_key = None
            return

        self.get_logger().warn(f'Clear failed: {response.message}')

    def _monster_key(self, monster: Dict) -> str:
        return str(monster.get('name', monster.get('id', 'unknown')))

    def _log_waiting(self, message: str) -> None:
        now = self.get_clock().now()
        if self.last_wait_log_time is not None:
            elapsed = (now - self.last_wait_log_time).nanoseconds * 1.0e-9
            if elapsed < 3.0:
                return
        self.last_wait_log_time = now
        self.get_logger().info(message)

    @staticmethod
    def _distance(a: Point2, b: Point2) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])


def main(args=None):
    rclpy.init(args=args)
    node = MonsterHunterNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
