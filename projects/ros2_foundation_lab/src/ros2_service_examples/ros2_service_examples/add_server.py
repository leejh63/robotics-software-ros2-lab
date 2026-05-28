import rclpy
from rclpy.node import Node
from ros2_foundation_interfaces.srv import AddTwoNum


class AddServer(Node):
    def __init__(self):
        super().__init__('add_two_num_server')
        self.srv = self.create_service(
            AddTwoNum, 'add_two_num', self.add_callback)
        self.get_logger().info('AddTwoNum service server started.')

    def add_callback(self, request, response):
        response.result = request.num1 + request.num2
        response.message = f'{request.num1} + {request.num2} = {response.result}'
        self.get_logger().info(
            f'Calculated: {request.num1} + {request.num2} = {response.result}')
        return response


def main():
    rclpy.init()
    node = AddServer()
    rclpy.spin(node)
    rclpy.shutdown()
