import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from ros2_foundation_interfaces.action import MoveDistance


class RobotMoveClient(Node):
    def __init__(self):
        super().__init__('robot_move_action_client')
        self._action_client = ActionClient(self, MoveDistance, 'move_robot')

    def send_goal(self, distance):
        goal_msg = MoveDistance.Goal()
        goal_msg.target_distance = distance
        self._action_client.wait_for_server()
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected by the action server.')
            return

        self.get_logger().info('Goal accepted by the action server.')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        distance = feedback_msg.feedback.current_distance
        self.get_logger().info(f'Feedback: current distance = {distance}')

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Final result: reached = {result.reached}')
        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = RobotMoveClient()
    node.send_goal(5.0)
    rclpy.spin(node)
