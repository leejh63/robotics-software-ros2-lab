import rclpy
from rclpy.node import Node
from ros2_foundation_interfaces.srv import LedControl


class LedServiceClient(Node):
    def __init__(self):
        super().__init__('led_service_client')
        self.cli = self.create_client(LedControl, 'set_led')
        # Wait until the service server is available.
        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for service...')
        self.req = LedControl.Request()

    def send_request(self, state):
        self.req.state = state
        self.future = self.cli.call_async(self.req)  # Send an asynchronous request.
        rclpy.spin_until_future_complete(self, self.future)  # Block until the future is complete.
        return self.future.result()


def main():
    rclpy.init()
    client = LedServiceClient()
    response = client.send_request(True)
    client.get_logger().info(
        f'Result: {response.success}, message: {response.message}')
    client.destroy_node()
    rclpy.shutdown()
