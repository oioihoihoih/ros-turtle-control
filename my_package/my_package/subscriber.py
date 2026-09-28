"""Read the first turtlesim turtle's pose."""

import argparse
import json
import sys
import time

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtlePoseSubscriber(Node):
    """Subscribe to the turtle pose for display or a one-time snapshot."""

    def __init__(self, once):
        super().__init__('turtle_pose_subscriber')
        self.once = once
        self.pose = None
        self.last_log_at = 0.0
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)

    def on_pose(self, pose):
        self.pose = pose
        if self.once:
            return
        now = time.monotonic()
        if now - self.last_log_at >= 0.5:
            self.get_logger().info(
                f'x={pose.x:.3f}, y={pose.y:.3f}, theta={pose.theta:.3f}')
            self.last_log_at = now


def main(args=None):
    parser = argparse.ArgumentParser(description='Read turtle position')
    parser.add_argument('--once', action='store_true',
                        help='Print one JSON pose and exit')
    options, ros_args = parser.parse_known_args(args)

    rclpy.init(args=ros_args)
    node = TurtlePoseSubscriber(options.once)
    try:
        if options.once:
            deadline = time.monotonic() + 5.0
            while rclpy.ok() and node.pose is None and time.monotonic() < deadline:
                rclpy.spin_once(node, timeout_sec=0.1)
            if node.pose is None:
                node.get_logger().error('No pose received from /turtle1/pose')
                return 1
            print(json.dumps({
                'x': node.pose.x,
                'y': node.pose.y,
                'theta': node.pose.theta,
            }))
        else:
            rclpy.spin(node)
        return 0
    except KeyboardInterrupt:
        return 0
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
