"""Reset turtlesim through its own /reset service."""

import sys

import rclpy
from rclpy.node import Node
from std_srvs.srv import Empty


class TurtleResetClient(Node):
    """Call the turtlesim reset service."""

    def __init__(self):
        super().__init__('turtle_reset_client')
        self.client = self.create_client(Empty, '/reset')

    def reset(self):
        if not self.client.wait_for_service(timeout_sec=5.0):
            self.get_logger().error('Start turtlesim_node first: /reset unavailable')
            return False
        future = self.client.call_async(Empty.Request())
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if not future.done() or future.exception() is not None:
            self.get_logger().error('The /reset request failed or timed out')
            return False
        self.get_logger().info('Turtlesim reset')
        return True


def main(args=None):
    rclpy.init(args=args)
    node = TurtleResetClient()
    try:
        return 0 if node.reset() else 1
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
