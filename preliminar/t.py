import queue
import sys
import os
import threading
import time
import openpyxl
import numpy as np
import serial
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Declare q como uma variável global
q1 = queue.Queue()  # usada para enviar as leituras para a MainWindow
q1_lock = threading.Lock()
print(q1_lock)
# q2 = queue.Queue() # usada para enviar as leituras para o LivePlot
# q2_lock = threading.Lock()
# print(q2_lock)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Strength Meter")

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Main layout (horizontal) to split the window
        main_layout = QHBoxLayout(main_widget)

        # Create a widget with buttons on the left side
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)

        # Add buttons
        self.start_button = QPushButton("Start Recording")
        self.export_button = QPushButton("Export")

        # Add a combo box for selecting the max time
        self.max_time_combobox = QComboBox()
        self.max_time_combobox.addItems(["3 seconds", "5 seconds", "10 seconds"])

        # Connect buttons to functions
        self.start_button.clicked.connect(self.toggle_recording)
        self.export_button.clicked.connect(lambda: self.export_to_excel(crucial=[]))

        # Add buttons to the widget's layout
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.export_button)
        button_layout.addWidget(self.max_time_combobox)

        # Add button widget to the main layout
        main_layout.addWidget(button_widget)

        # Create a widget with the plot on the right side
        self.plot_widget = LivePlotWidget()

        # Add the plot to the main layout
        main_layout.addWidget(self.plot_widget)

        # Set up the main layout
        main_widget.setLayout(main_layout)

        self.crucial = []

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Recording")
            max_time_text = self.max_time_combobox.currentText()
            max_time_seconds = int(max_time_text.split()[0])
            max_time_seconds += 2
            var = 0

            ts = threading.Thread(target=serialReaderThread, args=('COM5', max_time_seconds))
            ts.start()

            start_time = time.time()

            while (time.time() - start_time) < max_time_seconds:
                if not q1.empty():

                    with q1_lock:
                        output = q1.get()
                        var += 1
                        print(output, 'and', var)
                        self.crucial.append(output)
                time.sleep(0.01)
                print("Debug LivePlot")
                self.plot_widget.update_plot(self.crucial)
                print("Debug LivePlot 2")

            ts.join(timeout=max_time_seconds)

            if ts.is_alive():
                print("Thread ainda está ativa. Encerrando de maneira segura...")

            self.start_button.setText("Start Recording")

    def export_to_excel(self, patient):
        tw = threading.Thread(target=fileWriting, args=[self.crucial])
        tw.start()
        tw.join(timeout=10)

        if os.path.exists("output.txt"):
            os.remove("output.txt")

        with open("output.txt", "a+") as f:
            for position, value in enumerate(self.crucial):
                f.write(f"{value}\t{position}\n")


def serialReaderThread(port='COM6', recording_time=3):
        ser = serial.Serial(port, baudrate=57600, timeout=5)
        recording = True
        stopped = False
        max_recording_time = recording_time

        while not stopped:

            try:
                recording = True
                start_time = time.time()
                start_time2 = time.perf_counter()

                while recording and (time.time() - start_time) < max_recording_time:
                    # Read output from ser
                    output = float(ser.readline().decode('utf-8'))
                    print(output)
                    # Adicione a saída à fila
                    with q1_lock:
                        q1.put(output)
                        print(f"Queue {output}")

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time2
                print("Elapsed time: ", elapsed_time)
                recording = False
                stopped = True
                print("Recording stopped")

            except serial.SerialException as e:
                print(f"Erro na porta serial: {e}")


def fileWriting(crucial_data):
    try:
        stopped = False
        # max_recording_time = recording_time
        crucial = crucial_data

        workbook = openpyxl.Workbook()
        sheet = workbook.active

        for position, value in enumerate(crucial):
            sheet.append([position, value])

        file_path = r"D:\UDESC\TCC\Programas\GUIpreliminar\dados_do_paciente.xlsx"
        workbook.save(file_path)
        print(f"Data exported to Excel file: {file_path}")

        stopped = True
    except Exception as e:
        print(f"Erro durante a escrita do arquivo: {e}")


class LivePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QHBoxLayout(self)
        layout.addWidget(self.canvas)
        self.plot_line, = self.ax.plot([], [])
        self.y_values = [0, 0, 0]
        self.animation = FuncAnimation(self.figure, lambda: self.update_plot(interval=20, crucial=None), save_count=100, cache_frame_data=True)  # Atualiza a cada 20ms

    def update_plot(self, frame, crucial):
        if crucial is not None:
            self.y_values = crucial
            x_values = np.arange(len(self.y_values))
            print(self.y_values)
            print(x_values)

        if len(self.y_values) > 5:
            self.plot_line.set_data(x_values, self.y_values)
            self.ax.relim()
            self.ax.autoscale_view()
            self.canvas.draw()


def main():
    try:
        app = QApplication(sys.argv)
        window = MainWindow()

        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
