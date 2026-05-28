import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from ros2_foundation_interfaces.action import MoveDistance


class RobotMoveServer(Node):
    def __init__(self):
        super().__init__('robot_move_action_server')
        self._action_server = ActionServer(
            self, MoveDistance, 'move_robot', self.execute_callback)

    def execute_callback(self, goal_handle):
        self.get_logger().info('Starting target-distance action execution...')
        feedback_msg = MoveDistance.Feedback()
        feedback_msg.current_distance = 0.0
        target = goal_handle.request.target_distance

        for i in range(1, int(target) + 1):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return MoveDistance.Result(reached=False)

            time.sleep(1.0)
            feedback_msg.current_distance = float(i)
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f'Progress: {i}/{target}')

        goal_handle.succeed()
        result = MoveDistance.Result()
        result.reached = True
        return result


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(RobotMoveServer())
    rclpy.shutdown()
