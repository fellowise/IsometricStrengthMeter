import sys
import queue
import serial
import threading
import time
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QMutex, QMutexLocker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Declare q as uma variável global
q = queue.Queue()


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
        # self.plot_widget = LivePlotWidget()

        # Add the plot to the main layout
        main_layout.addWidget(self.plot_widget)

        # Set up the main layout
        main_widget.setLayout(main_layout)

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Stop Recording")

        else:
            self.start_button.setText("Start Recording")

    def export_to_excel(self, crucial, patient):

        file_thread = FileWriting()
        file_thread.start()
        file_thread.join(timeout=3)


class SerialReaderThread(threading.Thread):
    def __init__(self, parent=None, port='COM5', recording_time=3):
        super().__init__(parent)
        self.ser = serial.Serial(port, baudrate=57600, timeout=5)
        self.recording = True
        self.stopped = False
        self.max_recording_time = recording_time

    def run(self):

        while not self.stopped:

            try:
                self.recording = True
                start_time = time.time()

                while self.recording and (time.time() - start_time) < self.max_recording_time:
                    # Read output from ser
                    output = self.ser.readline().decode('utf-8')
                    print(output)
                    # Adicione a saída à fila
                    q.put(output)

                self.stop_recording()

            except serial.SerialException as e:
                print(f"Erro na porta serial: {e}")

    def stop_recording(self):
        self.recording = False
        self.stopped = True
        print("Recording stopped")


class FileWriting(threading.Thread):
    def __init__(self, parent=None, recording_time=3, crucial=None):
        super().__init__(parent)
        self.recording = True
        self.stopped = False
        self.max_recording_time = recording_time
        self.crucial = crucial

    def run(self):

        while not self.stopped:

            try:
                workbook = openpyxl.Workbook()
                sheet = workbook.active
                self.recording = True
                # start_time = time.time()

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


def main():
    try:
        data_reader = SerialReaderThread()

        # Inicie as threads
        data_reader.start()

        app = QApplication(sys.argv)
        window = MainWindow()

        window.show()
        sys.exit(app.exec())

        # Aguarde que as threads terminem (ou defina algum mecanismo para encerrar as threads quando necessário)
        data_reader.join(timeout=3)


        if thread.is_alive():
            print("Thread ainda está ativa. Encerrando de maneira segura...")

    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
