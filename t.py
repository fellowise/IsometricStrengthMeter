import sys
import serial
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Signal Animation")
        print("Hello world")
        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Create a vertical layout for the main widget
        layout = QVBoxLayout(main_widget)

        # Create a custom widget for data acquisition
        self.plot_widget = PlotWidget()
        layout.addWidget(self.plot_widget)

        # Create a custom widget for Excel export
        self.export_widget = ExportWidget()
        layout.addWidget(self.export_widget)

        # Set the layout for the main widget
        main_widget.setLayout(layout)


class PlotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.plot_line, = self.ax.plot([], [])
        self.animation = FuncAnimation(self.figure, self.update_plot, blit=True, interval=50)

        self.ax.set_xlim(0, 100)  # Assuming 100 data points
        self.ax.set_ylim(0, 1024)  # Assuming analog values range from 0 to 1023

        self.serial_port = "COM5"
        # Create a Serial object to communicate with Arduino
        self.arduino = serial.Serial(self.serial_port, 9600, timeout=1)
        self.data_buffer = np.zeros(100)

        # QTimer to update Arduino data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_arduino_data)
        self.timer.start(50)  # Update data every 50 ms

    def update_arduino_data(self):
        try:
            # Read value from pin A2 directly
            value = int(self.arduino.readline().decode('utf-8').strip())
            # Display the read value from pin A2
            print(f"Value from pin A2: {value}")

            # Update the data buffer
            self.data_buffer = np.roll(self.data_buffer, -1)
            self.data_buffer[-1] = value
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


class ExportWidget(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        # Add a button to trigger data export
        export_button = QPushButton("Export to Excel", self)
        export_button.clicked.connect(self.export_to_excel)
        layout.addWidget(export_button)

    def export_to_excel(self):
        # Create a new Excel workbook and select the active sheet
        wb = openpyxl.Workbook()
        sheet = wb.active

        # Sample data to export
        data = [
            ["Name", "Age", "City"],
            ["John", 25, "New York"],
            ["Alice", 30, "Paris"],
            ["Bob", 22, "London"]
        ]

        # Write data to the Excel sheet
        for row_data in data:
            sheet.append(row_data)

        # Save the workbook to a file
        wb.save("exported_data.xlsx")

        print("Data exported to Excel file.")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
