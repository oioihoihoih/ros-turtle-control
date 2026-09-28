"""Six-button PyQt5 frontend for the custom ROS 2 turtle nodes."""

import getpass
import json
import os
import sys

from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtWidgets import (
    QApplication, QGridLayout, QLabel, QMessageBox, QPushButton,
    QVBoxLayout, QWidget,
)


class TurtleControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ROS Turtle Control')
        self.setMinimumWidth(380)
        self.processes = set()

        self.status = QLabel('Start turtlesim_node, then press a button.')
        self.status.setWordWrap(True)
        self.status.setAlignment(Qt.AlignCenter)

        grid = QGridLayout()
        for label, direction, row, column in (
            ('↑ Up', 'up', 0, 1),
            ('← Left', 'left', 1, 0),
            ('↓ Down', 'down', 1, 1),
            ('→ Right', 'right', 1, 2),
        ):
            button = QPushButton(label)
            button.clicked.connect(
                lambda checked=False, value=direction: self.move(value))
            grid.addWidget(button, row, column)

        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset)
        grid.addWidget(reset_button, 2, 0)

        save_button = QPushButton('Save position')
        save_button.clicked.connect(self.save_position)
        grid.addWidget(save_button, 2, 1, 1, 2)

        layout = QVBoxLayout(self)
        layout.addLayout(grid)
        layout.addWidget(self.status)

    def run_node(self, executable, args=(), on_success=None):
        """Run only an executable defined in the new my_package package."""
        process = QProcess(self)
        process.setProgram('ros2')
        process.setArguments(['run', 'my_package', executable, *args])
        self.processes.add(process)

        def finished(exit_code, _exit_status):
            if process not in self.processes:
                return
            output = bytes(process.readAllStandardOutput()).decode(errors='replace')
            error = bytes(process.readAllStandardError()).decode(errors='replace')
            self.processes.discard(process)
            process.deleteLater()
            if exit_code != 0:
                self.show_error(error.strip() or output.strip() or
                                f'{executable} exited with code {exit_code}')
            elif on_success is not None:
                on_success(output)

        def failed(_error):
            if process not in self.processes:
                return
            self.processes.discard(process)
            process.deleteLater()
            self.show_error('Could not start ros2. Source the workspace first.')

        process.finished.connect(finished)
        process.errorOccurred.connect(failed)
        process.start()

    def move(self, direction):
        self.status.setText(f'Moving {direction}...')
        self.run_node('publisher', [direction],
                      lambda _output: self.status.setText(f'Moved {direction}'))

    def reset(self):
        self.status.setText('Resetting turtle...')
        self.run_node('reset', on_success=lambda _output:
                      self.status.setText('Turtle reset'))

    def save_position(self):
        self.status.setText('Reading turtle position...')
        self.run_node('subscriber', ['--once'], self.insert_position)

    def insert_position(self, output):
        try:
            pose = json.loads(output.strip().splitlines()[-1])
            import mysql.connector

            connection_args = {
                'user': os.getenv('MYSQL_USER', getpass.getuser()),
                'database': 'rosdb',
                'connection_timeout': 3,
            }
            if os.getenv('MYSQL_PASSWORD'):
                connection_args.update({
                    'host': os.getenv('MYSQL_HOST', '127.0.0.1'),
                    'port': int(os.getenv('MYSQL_PORT', '3306')),
                    'password': os.environ['MYSQL_PASSWORD'],
                })
            else:
                connection_args['unix_socket'] = os.getenv(
                    'MYSQL_SOCKET', '/var/run/mysqld/mysqld.sock')

            connection = mysql.connector.connect(**connection_args)
            try:
                cursor = connection.cursor()
                try:
                    cursor.execute(
                        'INSERT INTO turtlepos (`x`, `y`, `theta`) '
                        'VALUES (%s, %s, %s)',
                        (pose['x'], pose['y'], pose['theta']),
                    )
                    connection.commit()
                    row_id = cursor.lastrowid
                finally:
                    cursor.close()
            finally:
                connection.close()
            self.status.setText(
                f'Saved #{row_id}: x={pose["x"]:.3f}, '
                f'y={pose["y"]:.3f}, theta={pose["theta"]:.3f}')
        except Exception as error:
            self.show_error(str(error))

    def show_error(self, message):
        self.status.setText('Error: ' + message)
        QMessageBox.warning(self, 'Turtle control', message)

    def closeEvent(self, event):
        for process in list(self.processes):
            process.kill()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = TurtleControl()
    window.show()
    return app.exec_()


if __name__ == '__main__':
    sys.exit(main())
