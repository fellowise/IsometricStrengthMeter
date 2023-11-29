import queue
import sys
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import openpyxl
import serial
from PyQt5.QtCore import QMutex, QMutexLocker
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Declare q as uma variável global
q1 = queue.Queue() # usada para enviar as leituras para a MainWindow
q1_mutex = QMutex()
q2 = queue.Queue() # usada para enviar as leituras para o LivePlot
q2_mutex = QMutex()


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
        self.export_button.clicked.connect(self.export_to_excel)

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

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Stop Recording")
            max_time_text = self.max_time_combobox.currentText()
            max_time_seconds = int(max_time_text.split()[0])
            var = 0
            crucial = []
            ts = threading.Thread(target=SerialReaderThread, args=('COM5', max_time_seconds))
            print("First Debug")
            ts.start()
            start_time = time.time()

            while (time.time() - start_time) < max_time_seconds:
                output = q1.get()
                var += 1
                print(output, 'and', var)
                crucial.append(output)

                with open("output.txt", "a+") as f:
                    f.write(crucial, "\t", var)
                    f.write("\n")  # Se quiser separar as saídas por novas linhas
            ts.join(timeout=max_time_seconds)

            if ts.is_alive():
                print("Thread ainda está ativa. Encerrando de maneira segura...")

        else:
            self.start_button.setText("Start Recording")

    def export_to_excel(self, crucial, patient):

        file_thread = FileWriting()
        file_thread.start()
        file_thread.join(timeout=3)


def SerialReaderThread(port='COM5', recording_time=3):
        ser = serial.Serial(port, baudrate=57600, timeout=5)
        recording = True
        stopped = False
        max_recording_time = recording_time

        while not stopped:

            try:
                recording = True
                start_time = time.time()
                start_time2 = time.perf_counter()
                print("Second Debug")

                while recording and (time.time() - start_time) < max_recording_time:
                    # Read output from ser
                    output = ser.readline().decode('utf-8')
                    print(time.time())
                    print(output)
                    # Adicione a saída à fila
                    with QMutexLocker(q1_mutex):
                        q1.put(output)
                    with QMutexLocker(q2_mutex):
                        q2.put(output)
                    print("3rd debug")

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                print("Elapsed time: ", elapsed_time)
                recording = False
                stopped = True
                print("Recording stopped")

            except serial.SerialException as e:
                print(f"Erro na porta serial: {e}")


class FileWriting(threading.Thread):
    def __init__(self, parent=None, recording_time=3, crucial=None):
        super().__init__(parent)
        self.recording = True
        self.stopped = False
        self.max_recording_time = recording_time
        self.crucial = []

    def run(self):

        while not self.stopped:

            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                self.recording = True
                # start_time = time.time()
                with QMutexLocker(q1_mutex):
                    self.crucial.extend(q1.get())
                # while self.recording and (time.time() - start_time) < self.max_recording_time:
                    # output = q.get()  # Espera até que um item esteja disponível na fila

                for position, value in enumerate(self.crucial):
                    sheet.append([position, value])

                file_path = r"D:\UDESC\TCC\Programas\GUIpreliminar\dados_do_paciente.xlsx"
                workbook.save(file_path)
                print(f"Data exported to Excel file: {file_path}")

                self.stop_recording()
            except Exception as e:
                print(f"Erro durante a escrita do arquivo: {e}")

    def stop_recording(self):
        self.recording = False
        self.stopped = True
        print("Recording stopped")


class LivePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QHBoxLayout(self)
        layout.addWidget(self.canvas)
        self.plot_line, = self.ax.plot([], [])

    def update_plot(self):
        while True:
            with QMutexLocker(q2_mutex):
                if not q2.empty():
                    y_values = q2.get()
                    x_values = np.arange(len(y_values))
                    self.plot_line.set_data(x_values, y_values)
                    self.ax.relim()
                    self.ax.autoscale_view()
                    self.canvas.draw()
##
#        print("Debug fila")
#        if not q2.empty():
#            print("Debug 3")
#            with q2_lock:
#                print("debug 4")
#                self.y_values.append(q2.get())
#                print("Debug 5")
#                x_values = np.arange(len(self.y_values))
#                print(x_values)
#                print(self.y_values)
#                self.plot_line.set_data(x_values, self.y_values)
#                print("Debug 6")
#                if len(self.y_values) > 5:
#                    self.ax.relim()
#                    print("Debug 7")
#                    self.ax.autoscale_view()
#                    print("Debug 8")
#                    self.canvas.draw()
#                    print("Debug 9")
##

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
