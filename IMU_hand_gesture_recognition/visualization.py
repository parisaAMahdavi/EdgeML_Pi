from PyQt5 import QtWidgets, QtCore, QtGui
from pyqtgraph import PlotWidget
import pyqtgraph as pg

import sys

import numpy
from collections import deque
from IMU import GY85_IMUSensor

   
# Time and Sampling settings
time_interval = 0.01  # 10ms (100 Hz sampling)
buffer_size = 100  # Keep last 100 data points
imu = GY85_IMUSensor()
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setGeometry(100, 100, 1000, 800)

        self.centralWidget = QtWidgets.QWidget()
        self.setCentralWidget(self.centralWidget)
        layout = QtWidgets.QVBoxLayout(self.centralWidget)

        # Create plots
        self.graphWidget_gyro = pg.PlotWidget(title="Gyroscope Data")
        self.graphWidget_accel = pg.PlotWidget(title="Accelerometer Data")

        layout.addWidget(self.graphWidget_gyro)
        layout.addWidget(self.graphWidget_accel)

        # Data buffers
        self.time_data = deque(maxlen=buffer_size)
        self.gyro_x_data = deque(maxlen=buffer_size)
        self.gyro_y_data = deque(maxlen=buffer_size)
        self.gyro_z_data = deque(maxlen=buffer_size)
        self.accel_x_data = deque(maxlen=buffer_size)
        self.accel_y_data = deque(maxlen=buffer_size)
        self.accel_z_data = deque(maxlen=buffer_size)

        # Set plot backgrounds to white
        for graph in [self.graphWidget_gyro, self.graphWidget_accel]:
            graph.setBackground(QtGui.QColor(255, 255, 255))

        # Set axis labels
        self.graphWidget_gyro.setLabels(bottom="Time (s)", left="Gyroscope (°/s)")
        self.graphWidget_accel.setLabels(bottom="Time (s)", left="Accelerometer (g)")

        # Create a shared legend and place it inside the first plot (but outside the graph area)
        self.legend = pg.LegendItem((30, 30), offset=(30, 5))  # (width, height), (x, y) offset
        self.legend.setParentItem(self.graphWidget_gyro.getPlotItem())  # Attach to Gyro plot

        # Create plot lines
        self.line_gyro_x = self.graphWidget_gyro.plot([], [], pen=pg.mkPen(color='r'))
        self.line_gyro_y = self.graphWidget_gyro.plot([], [], pen=pg.mkPen(color='g'))
        self.line_gyro_z = self.graphWidget_gyro.plot([], [], pen=pg.mkPen(color='b'))

        self.line_accel_x = self.graphWidget_accel.plot([], [], pen=pg.mkPen(color='r'))
        self.line_accel_y = self.graphWidget_accel.plot([], [], pen=pg.mkPen(color='g'))
        self.line_accel_z = self.graphWidget_accel.plot([], [], pen=pg.mkPen(color='b'))

         # Add all items to the shared legend
        self.legend.addItem(self.line_gyro_x, "X")
        self.legend.addItem(self.line_gyro_y, "Y")
        self.legend.addItem(self.line_gyro_z, "Z")
    

        # Timer for updating plot
        self.timer = QtCore.QTimer()
        self.timer.setInterval(int(time_interval * 1000))  # Convert to milliseconds
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

    def update_plot_data(self):

        # Ensure time increases correctly
        if len(self.time_data) == 0:
            self.time_data.append(0)
        else:
            self.time_data.append(self.time_data[-1] + time_interval)

        # Read sensor data
        gyroscope = numpy.array(imu.get_gyro_data())  
        accelerometer = numpy.array(imu.get_accel_data())

        # Append new data
        self.gyro_x_data.append(gyroscope[0])
        self.gyro_y_data.append(gyroscope[1])
        self.gyro_z_data.append(gyroscope[2])

        self.accel_x_data.append(accelerometer[0])
        self.accel_y_data.append(accelerometer[1])
        self.accel_z_data.append(accelerometer[2])

        # Update plots with latest data
        self.line_gyro_x.setData(self.time_data, self.gyro_x_data)
        self.line_gyro_y.setData(self.time_data, self.gyro_y_data)
        self.line_gyro_z.setData(self.time_data, self.gyro_z_data)

        self.line_accel_x.setData(self.time_data, self.accel_x_data)
        self.line_accel_y.setData(self.time_data, self.accel_y_data)
        self.line_accel_z.setData(self.time_data, self.accel_z_data)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

"""To see PyQtGraph directly on your desktop via SSH, follow these steps or use VNC Viewer to view the GUI on your computer.
*Using X11 forwarding over SSH (make sure your system has X11 installed)
1. Enable X11 Forwarding on Raspberry Pi:
    1. Via raspi-config or install X11 on raspi if it is not installed 
    2. After installing enable X11 Forwarding in SSH:
        1. Open the SSH config file: 'sudo nano /etc/ssh/sshd_config'
        2. Find and uncomment (or add) these lines:
            1. X11Forwarding yes
            2. X11DisplayOffset 10
        3. Save and exit
        4. Restart SSH service using: 'sudo systemctl restart ssh'
2. Connect to your raspi via x11 forwarding: 'ssh -X pi@<RaspberryPi_IP>'
3. Run Your PyQtGraph Script on the Pi """
