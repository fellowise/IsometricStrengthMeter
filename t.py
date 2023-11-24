import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
import serial

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Signal Animation")

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Main layout (horizontal) to split the window
        main_layout = QHBoxLayout(main_widget)

        # Create a widget with buttons on the left side
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)

        # Add buttons
        self.start_button = QPushButton("Start Recording")
        self.pause_button = QPushButton("Export")

        # Connect buttons to functions
        self.start_button.clicked.connect(self.toggle_recording)
        self.pause_button.clicked.connect(self.export_to_excel)

        # Add buttons to the widget's layout
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)

        # Add button widget to the main layout
        main_layout.addWidget(button_widget)

        # Create a widget with the plot on the right side
        self.plot_widget = PlotWidget()

        # Add the plot to the main layout
        main_layout.addWidget(self.plot_widget)

        # Set up the main layout
        main_widget.setLayout(main_layout)

        # Create a Serial object to communicate with Arduino
        self.serial_port = "COM6"
        self.arduino = serial.Serial(self.serial_port, 57600, timeout=1)

        # Additional attributes
        self.recording = False
        self.max_time_seconds = 10  # Adjust the value as needed
        self.peak_value = 0
        self.peak_index = 0

        # QTimer to update Arduino data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_arduino_data)
        self.timer.start(80)  # Update data every X ms

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Stop Recording")
            self.plot_widget.start_recording()
        else:
            self.start_button.setText("Start Recording")
            crucial_data = self.plot_widget.stop_recording()
            self.export_to_excel(crucial_data, patient="John Doe")

    def export_to_excel(self, crucial, patient):
        # Implement exporting data to Excel
        pass

    def update_arduino_data(self):
        try:
            # Read value from the Arduino over the serial port
            data_float = float(self.arduino.readline().decode('utf-8').strip())
            print("Debug 1")
            print(data_float)
            if data_float:
                value = float(data_float)
                print(value)
                if self.recording and (len(self.data_buffer) / 50) < (self.max_time_seconds * 50):
                    self.data_buffer = np.roll(self.data_buffer, -1)
                    self.data_buffer[-1] = value
                    print("Debug 3")

                    # Update peak value and index if a new peak is found
                    if value > self.peak_value:
                        self.peak_value = value
                        self.peak_index = len(self.data_buffer) - 1
                        print("Debug 4")
        except KeyboardInterrupt:
            # Close the serial communication when pressing Ctrl+C
            self.arduino.close()
            print("Serial communication closed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.data_buffer = []
        self.recording = False

        # Additional attributes
        self.max_time_seconds = 10  # Adjust the value as needed
        self.peak_value = 0
        self.peak_index = 0

        self.plot_line, = self.ax.plot([], [])

        self.ax.set_xlim(0, 1000)  # Assuming 1000 data points
        self.ax.set_ylim(0, 1024)  # Assuming analog values range from 0 to 1023

        self.animation = FuncAnimation(self.figure, self.update_plot, blit=True, interval=80, cache_frame_data=True, save_count=1000)

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        self.recording = False
        return self.data_buffer

    def update_data(self, value):
        if self.recording:
            self.data_buffer.append(value)
            if len(self.data_buffer) > 1000:  # Limit the buffer size for display purposes
                self.data_buffer.pop(0)

    def update_plot(self, _):
        x = np.arange(len(self.data_buffer))
        y = self.data_buffer
        self.plot_line.set_data(x, y)
        return self.plot_line,


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()
