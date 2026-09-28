# ros-turtle-control

ROS 2 Humble turtlesim exercise. The repository contains only the custom ROS
package, the six-button PyQt5 application, and the MySQL schema script.

```text
ros-turtle-control/
├── my_package/              # ROS 2 Python package and its own nodes
├── PyQt/
│   ├── turtle_gui.py        # four directions, reset, save position
│   └── README.md
├── db/
│   └── create_rosdb.sql     # rosdb.turtlepos schema
├── README.md
└── .gitignore
```

Only `turtlesim_node` is run from an existing ROS package. Movement, pose
reading, and reset are implemented in `my_package`. The arrow buttons move in
screen directions without changing the turtle's angle. The older practice
packages `my_first_package` and `my_first_package_msgs` are not used at runtime.

## Build

From the repository root in Ubuntu 22.04 with ROS 2 Humble installed:

```bash
source /opt/ros/humble/setup.bash
colcon build --packages-select my_package
source install/setup.bash
```

Follow [PyQt/README.md](PyQt/README.md) to set up MySQL and run the app.
