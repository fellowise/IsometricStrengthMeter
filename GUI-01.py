import queue
import sys
import os
import threading
import time
import openpyxl
import numpy as np
import serial
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QPushButton, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

# Declare q como uma variável global
q1 = queue.Queue()  # usada para enviar as leituras para a MainWindow
q1_lock = threading.Lock()
print(q1_lock)


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

        self.crucial = []
        self.recording_time = 3    # 3 segundos como default

    def toggle_recording(self):
        if self.start_button.text() == "Start Recording":
            self.start_button.setText("Recording")
            self.crucial = []
            max_time_text = self.max_time_combobox.currentText()
            max_time_seconds = int(max_time_text.split()[0])
            self.recording_time = 5 + max_time_seconds
            var = 0

            ts = threading.Thread(target=serialReaderThread, args=('COM6', self.recording_time))
            ts.start()

            start_time = time.time()

            while (time.time() - start_time) < self.recording_time:
                if not q1.empty():

                    with q1_lock:
                        output = q1.get()
                        var += 1
                        print(output, 'and', var)
                        self.crucial.append(output)
                # time.sleep(0.02)
            # print("Debug LivePlot")
            self.plot_widget.update_plot(self.crucial, self.recording_time)
            # print("Debug LivePlot 2")

            ts.join(timeout=max_time_seconds)

            if ts.is_alive():
                print("Thread ainda está ativa. Encerrando de maneira segura...")

            self.start_button.setText("Start Recording")

    def export_to_excel(self):
        recording_time = self.recording_time - 5
        tw = threading.Thread(target=fileWriting, args=[self.crucial, recording_time])
        tw.start()
        tw.join(timeout=10)

        if os.path.exists("output.txt"):
            os.remove("output.txt")

        with open("output.txt", "a+") as f:
            for position, value in enumerate(self.crucial):
                max_time_text = self.max_time_combobox.currentText()
                max_time_seconds = int(max_time_text.split()[0])
                factor = max_time_seconds/max(position)
                test_time = position*factor
                f.write(f"{test_time}\t{value}\n")


def serialReaderThread(port='COM5', recording_time=3):
        ser = serial.Serial(port, baudrate=57600, timeout=5)
        recording = True
        stopped = False
        max_recording_time = recording_time
        # ser.write(b'r')

        while not stopped:

            try:
                recording = True
                start_time = time.time()
                start_time2 = time.perf_counter()

                while recording and (time.time() - start_time) < max_recording_time:
                    # Read output from ser
                    # print(ser.readline().decode('utf-8'))
                    output = float(ser.readline().decode('utf-8'))
                    # print(output)
                    # Adicione a saída à fila
                    with q1_lock:
                        q1.put(output)

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time2
                print("Elapsed time: ", elapsed_time)
                recording = False
                stopped = True
                print("Recording stopped")

            except serial.SerialException as e:
                print(f"Erro na porta serial: {e}")


def fileWriting(crucial_data, recording_time):
    try:
        crucial = crucial_data

        workbook = openpyxl.Workbook()
        sheet = workbook.active
        # print(len(crucial_data))
        factor = recording_time / len(crucial_data)

        for position, value in enumerate(crucial):
            test_time = position*factor
            sheet.append([test_time, value])

        file_path = r"D:\UDESC\TCC\Programas\GUIpreliminar\dados_do_paciente.xlsx"
        workbook.save(file_path)
        print(f"Data exported to Excel file: {file_path}")

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
        self.y_values = []
        self.threshold = 0.4
        plt.xlabel('Time (s)')
        plt.ylabel('Strength (kgf)')

    def update_plot(self, crucial, recording_time):
        self.y_values = crucial
        x_index = np.arange(len(self.y_values))
        factor = (recording_time-5)/max(x_index)
        x_values = x_index*factor
        print(self.y_values)
        print(x_values)

        if len(self.y_values) > 5:
            self.plot_line.set_data(x_values, self.y_values)

            # Lógica de Pico
            peak_index = np.argmax(self.y_values)
            peak_value = self.y_values[peak_index]
            peak_time = x_values[peak_index]

            plt.scatter(peak_time, peak_value, color='red', label='Max Strength')
            plt.annotate(f'Max Strength: {peak_value:.2f} kgf',
                         xy=(x_values[peak_index], peak_value),
                         xytext=(x_values[peak_index]+0.1, peak_value+0.1))

            # Limite inferior e tempo de reação
            plt.axhline(y=self.threshold, color='black', linestyle='--', label='Threshold')
            reactions = []
            for i, value in enumerate(self.y_values):
                if value > self.threshold:
                    reactions.append(i)


            reaction_index = min(reactions)
            reaction_time = x_values[reaction_index]
            reaction_value = self.y_values[reaction_index]
            print("Vamo pra janta")
            print(reactions)
            print(reaction_time)
            print(reaction_value)
            plt.scatter(reaction_time, reaction_value, color='green', label='Reaction Time')
            plt.annotate(f'Reaction Time: {reaction_time:.2f} s',
                         xy=(reaction_time, reaction_value),
                         xytext=(reaction_time+0.1, reaction_value+0.1))

            # Taxa de Desenvolvimento
            x_development = [reaction_time, peak_time]
            y_development = [reaction_value, peak_value]
            development_rate = (peak_value-reaction_value)/(peak_time-reaction_time)
            plt.plot(x_development, y_development, linestyle='--', color='gray', linewidth=2, label='Development Rate')
            plt.annotate(f'Development Rate: {development_rate:.2f} kgf/s',
                         xy=(x_values[peak_index], peak_value),
                         xytext=(x_values[peak_index] + 0.1, np.mean(np.array([peak_value, reaction_value]))))

            # Taxa de declínio
            # tem que usar um ponto flutuante entre o pico e o fim do sinal
            # print("Vamo")
            # print("Pra")
            # print("Janta")
            # print("abalados")
            # print("ou campeões")
            # print("Não tem")
            # print("meio termo")
            declines = []
            decline_time = []
            decline_values = []
            desired_fit = 10
            for i, value in enumerate(self.y_values):
                if i > peak_index and i+desired_fit < len(x_values):
                    declines.append(i)
                    decline_time.append(x_values[i])
                    decline_values.append(value)

            print(declines)
            print(decline_time)
            print(decline_values)
            linear_regression = np.polyfit(decline_time, decline_values, 1)
            print(linear_regression)
            decline_coefficients = np.poly1d(linear_regression)
            decline_plot_value = decline_coefficients(decline_time)
            print(min(decline_values))
            print(min(decline_time))
            decline_rate = (min(decline_values)-peak_value)/(max(decline_time)-peak_time)
            # plt.scatter(decline_time, decline_value, label='Decline Rate')
            plt.plot(decline_time, decline_plot_value, color='red', linestyle='--', label='Decline Rate Prediction')
            plt.annotate(f'Decline Rate: {decline_rate:.2f} kgf/s',
                         xy=(x_values[peak_index], peak_value),
                         xytext=(max(decline_time)-1, np.mean(np.array([peak_value, min(decline_values)]))))

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
