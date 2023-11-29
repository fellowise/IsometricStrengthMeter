import queue
import sys
import os
import threading
import time

import numpy as np
import serial
from PyQt5.QtCore import QMutex, QMutexLocker

# Declare q as uma variável global
q1 = queue.Queue() # usada para enviar as leituras para a MainWindow
q1_mutex = QMutex()


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

                while recording and (time.time() - start_time) < max_recording_time:
                    # Read output from ser
                    output = ser.readline().decode('utf-8')
                    print(output)
                    # Adicione a saída à fila
                    with QMutexLocker(q1_mutex):
                        q1.put(output)

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time2
                print("Elapsed time: ", elapsed_time)
                recording = False
                stopped = True
                print("Recording stopped")

            except serial.SerialException as e:
                print(f"Erro na porta serial: {e}")


def main():
    try:
        max_time_seconds = 3
        var = 0
        crucial = []
        ts = threading.Thread(target=SerialReaderThread, args=('COM5', max_time_seconds))
        ts.start()
        start_time = time.time()

        while (time.time() - start_time) < max_time_seconds:
            output = q1.get()
            var += 1
            print(output, 'and', var)
            crucial.append(output)

        ts.join(timeout=max_time_seconds)

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
