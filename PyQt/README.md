# PyQt turtle controller

This app has six buttons: up, down, left, right, reset, and save position.
Each button runs an executable from the custom `my_package` ROS package.

## Dependencies

In Ubuntu 22.04:

```bash
sudo apt update
sudo apt install mysql-server python3-mysql.connector python3-pyqt5
sudo systemctl start mysql
```

From the `ros-turtle-control` repository root, create the database and give
the local Ubuntu user `wlgh` access through the MySQL Unix socket:

```bash
sudo mysql < db/create_rosdb.sql
sudo mysql -e "CREATE USER IF NOT EXISTS 'wlgh'@'localhost' IDENTIFIED WITH auth_socket; GRANT SELECT, INSERT ON rosdb.* TO 'wlgh'@'localhost';"
```

For another Ubuntu username, replace `wlgh` in the SQL command. MySQL fills
the `id` and `time` columns automatically when Save position inserts the
current `x`, `y`, and `theta`.

## Run

Terminal 1:

```bash
source /opt/ros/humble/setup.bash
ros2 run turtlesim turtlesim_node
```

Terminal 2, from the repository root:

```bash
source install/setup.bash
python3 PyQt/turtle_gui.py
```

For a MySQL server on another host, set `MYSQL_HOST`, `MYSQL_PORT`,
`MYSQL_USER`, and `MYSQL_PASSWORD` before launching the app. For a local
socket, `MYSQL_SOCKET` can override `/var/run/mysqld/mysqld.sock`.
