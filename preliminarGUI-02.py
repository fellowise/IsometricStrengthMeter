import sys
import serial
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer


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

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Stop Recording")
            self.plot_widget.start_recording()
        else:
            self.start_button.setText("Start Recording")
            crucial_data = self.plot_widget.stop_recording()
            self.export_to_excel(crucial_data, patient="John Doe")

    def export_to_excel(self, crucial, patient):
        # Create a new Excel workbook and select the active sheet
        wb = openpyxl.Workbook()
        sheet = wb.active

        # Sample data to export
        data = [
            ["Name", "Strength Peak", "Development of Strength", "Decline Rate"],
            [patient, crucial[0], crucial[1], crucial[2]],
        ]

        # Write data to the Excel sheet
        for row_data in data:
            sheet.append(row_data)

        # Specify the full path where you want to save the Excel file
        file_path = r"D:\UDESC\TCC\Programas\GUIpreliminar\dados_do_paciente.xlsx"

        # Save the workbook to the specified file path
        wb.save(file_path)

        print(f"Data exported to Excel file: {file_path}")


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.data_buffer = np.zeros(1000)
        self.recording = False

        self.plot_line, = self.ax.plot([], [])
        self.animation = FuncAnimation(self.figure, self.update_plot, blit=True, interval=10, cache_frame_data=True)

        self.ax.set_xlim(0, 1000)  # Assuming 1000 data points
        self.ax.set_ylim(0, 1024)  # Assuming analog values range from 0 to 1023

        self.serial_port = "COM5"
        # Create a Serial object to communicate with Arduino
        self.arduino = serial.Serial(self.serial_port, 115200, timeout=1)

        # QTimer to update Arduino data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_arduino_data)
        self.timer.start(10)  # Update data every 20 ms

        self.peak_value = 0
        self.peak_index = 0

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        self.recording = False

        # Find peak index using np.argmax
        self.peak_index = np.argmax(self.data_buffer)
        # Extract and return relevant data for export
        crucial_data = [
            round(float(self.peak_value), 1),
            round(float(self.calculate_gradient_to_peak()), 1),
            round(float(self.calculate_gradient_after_peak()), 1),
        ]

        # Reset peak value and index
        self.peak_value = 0
        self.peak_index = 0

        return crucial_data

    def calculate_gradient_to_peak(self):
        if self.peak_index == 0:
            return 0  # Cannot calculate gradient without a peak

        # Calculate the gradient from the bottom to the peak using np.mean(np.gradient())
        gradient = np.mean(np.gradient(self.data_buffer[: self.peak_index + 1]))
        return gradient

    def calculate_gradient_after_peak(self):
        if self.peak_index == 0:
            return 0  # Cannot calculate gradient without a peak

        # Calculate the gradient from the peak to the next 3 seconds of the signal using np.mean(np.gradient())
        x1 = self.peak_index
        x2 = self.peak_index + 100  # Assuming 3 seconds with 50 data points per second
        gradient = np.mean(np.gradient(self.data_buffer[x1:x2 + 1]))
        return gradient

    def update_arduino_data(self):
        try:
            # Read value from pin A2 directly
            data_str = self.arduino.readline().decode('utf-8').strip()

            if data_str:
                value = int(data_str)
                # Update the data buffer if recording
                if self.recording:
                    self.data_buffer = np.roll(self.data_buffer, -1)
                    self.data_buffer[-1] = value

                    # Update peak value and index if a new peak is found
                    if value > self.peak_value:
                        self.peak_value = value
                        self.peak_index = len(self.data_buffer) - 1

        except KeyboardInterrupt:
            # Close the serial communication when pressing Ctrl+C
            self.arduino.close()
            print("Serial communication closed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

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
