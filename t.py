import queue
import sys
import os
import threading
import time
import openpyxl
import numpy as np
import serial
# import matplotlib.pyplot as plt
from PyQt5.QtCore import QMutex, QMutexLocker
# from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QComboBox
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Declare q como uma variável global
q1 = queue.Queue()  # usada para enviar as leituras para a MainWindow
q1_mutex = QMutex()
# q2 = queue.Queue() # usada para enviar as leituras para o LivePlot
# q2_mutex = QMutex()


def serialReaderThread(port='COM5', recording_time=3):
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
                    output = ser.readline().decode('utf-8')
                    print(output)
                    # Adicione a saída à fila
                    with QMutexLocker(q1_mutex):
                        q1_mutex.lock()
                        print("Debug 1")
                        q1.put(output)
                        print("Debug 2")
                        q1_mutex.unlock()
                        print("Debug 3")
                    # with QMutexLocker(q2_mutex):
                    #     q2.put(output)

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


def main():
    try:
        max_time_seconds = 3
        var = 0
        crucial = []

        ts = threading.Thread(target=serialReaderThread, args=('COM5', max_time_seconds))
        ts.start()

        start_time = time.time()
        print("Debug 4")
        while (time.time() - start_time) < max_time_seconds:
            if not q1.empty():
                print("Debug 5")
                with QMutexLocker(q1_mutex):
                    output = q1.get()
                    print("Debug 6")
                    var += 1
                    print(output, 'and', var)
                    crucial.append(output)

        ts.join(timeout=max_time_seconds)

        tw = threading.Thread(target=fileWriting, args=crucial)
        tw.start()
        tw.join(timeout=10)

        if ts.is_alive():
            print("Thread ainda está ativa. Encerrando de maneira segura...")

        if os.path.exists("output.txt"):
            os.remove("output.txt")

        with open("output.txt", "a+") as f:
            for position, value in enumerate(crucial):
                f.write(f"{value}\t{position}\n")

    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
