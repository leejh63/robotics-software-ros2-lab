import rclpy
from rclpy.node import Node
from ros2_foundation_interfaces.srv import AddTwoNum


class AddClient(Node):
    def __init__(self):
        super().__init__('add_two_num_client')
        self.cli = self.create_client(AddTwoNum, 'add_two_num')
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        self.req = AddTwoNum.Request()

    def send_request(self, num1, num2):
        self.req.num1 = num1
        self.req.num2 = num2
        self.future = self.cli.call_async(self.req)
        rclpy.spin_until_future_complete(self, self.future)
        return self.future.result()


def main():
    rclpy.init()
    client = AddClient()
    response = client.send_request(5, 10)
    client.get_logger().info(f'Result: {response.result}, message: {response.message}')
    client.destroy_node()
    rclpy.shutdown()
