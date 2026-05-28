import rclpy
from rclpy.node import Node
from ros2_foundation_interfaces.srv import LedControl


class LedServiceServer(Node):
    def __init__(self):
        super().__init__('led_service_server')
        self.srv = self.create_service(
            LedControl, 'set_led', self.set_led_callback)
        self.get_logger().info('LED service server started.')

    def set_led_callback(self, request, response):
        if request.state:
            self.get_logger().info('Received LED ON request.')
            response.success = True
            response.message = "LED turned on."
        else:
            self.get_logger().info('Received LED OFF request.')
            response.success = True
            response.message = "LED turned off."
        return response  # A service callback must return the response object.


def main():
    rclpy.init()
    node = LedServiceServer()
    rclpy.spin(node)
    rclpy.shutdown()
