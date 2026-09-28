"""Move the turtle in a screen direction without turning it."""

import argparse
import math
import sys
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from turtlesim.msg import Pose


class TurtleMovePublisher(Node):
    """Convert screen direction into turtle-frame linear velocity."""

    def __init__(self, direction, duration):
        super().__init__('turtle_move_publisher')
        self.publisher = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Pose, '/turtle1/pose', self.on_pose, 10)
        self.direction = direction
        self.duration = duration
        self.theta = None
        self.created_at = time.monotonic()
        self.started_at = None
        self.done = False
        self.succeeded = False
        self.timer = self.create_timer(0.05, self.on_timer)

    def on_pose(self, pose):
        self.theta = pose.theta

    def on_timer(self):
        now = time.monotonic()
        if self.publisher.get_subscription_count() == 0 or self.theta is None:
            if now - self.created_at >= 5.0:
                self.get_logger().error('Start turtlesim_node first')
                self.done = True
            return

        if self.started_at is None:
            self.started_at = now

        if now - self.started_at >= self.duration:
            self.publisher.publish(Twist())
            self.get_logger().info('Stopped turtle')
            self.succeeded = True
            self.done = True
            return

        command = Twist()
        speed = 2.0
        if self.direction == 'up':
            world_x, world_y = 0.0, speed
        elif self.direction == 'down':
            world_x, world_y = 0.0, -speed
        elif self.direction == 'left':
            world_x, world_y = -speed, 0.0
        else:
            world_x, world_y = speed, 0.0

        heading_cos = math.cos(self.theta)
        heading_sin = math.sin(self.theta)
        command.linear.x = heading_cos * world_x + heading_sin * world_y
        command.linear.y = -heading_sin * world_x + heading_cos * world_y
        self.publisher.publish(command)


def main(args=None):
    parser = argparse.ArgumentParser(description='Move turtle: up/down/left/right')
    parser.add_argument('direction', choices=('up', 'down', 'left', 'right'))
    parser.add_argument('--duration', type=float, default=0.5,
                        help='Movement time in seconds (default: 0.5)')
    options, ros_args = parser.parse_known_args(args)
    if options.duration <= 0:
        parser.error('--duration must be greater than zero')

    rclpy.init(args=ros_args)
    node = TurtleMovePublisher(options.direction, options.duration)
    try:
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=0.1)
        return 0 if node.succeeded else 1
    except KeyboardInterrupt:
        node.publisher.publish(Twist())
        return 130
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    sys.exit(main())
