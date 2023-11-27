import sys
import serial
import threading
import numpy as np
import openpyxl
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QWidget, QVBoxLayout, QPushButton, \
    QComboBox
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QMutex
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Strength Meter")

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Main layout (horizontal) to split the window
        main_layout = QVBoxLayout(main_widget)

        # Create a widget with buttons on the left side
        button_widget = QWidget()
        button_layout = QVBoxLayout(button_widget)

        # Add buttons
        self.start_button = QPushButton("Start Recording")
        self.pause_button = QPushButton("Export")

        # Add a combo box for selecting the max time
        self.max_time_combobox = QComboBox()
        self.max_time_combobox.addItems(["3 seconds", "5 seconds", "10 seconds"])

        # Connect buttons to functions
        self.start_button.clicked.connect(self.toggle_recording)
        self.pause_button.clicked.connect(self.export_to_excel)

        # Add buttons to the widget's layout
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.pause_button)
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
            self.plot_widget.start_recording()

            # Get the selected max time from the combo box
            max_time_text = self.max_time_combobox.currentText()
            max_time_seconds = int(max_time_text.split()[0])  # Extract the numeric value
            self.plot_widget.set_max_time(max_time_seconds)
        else:
            self.start_button.setText("Start Recording")
            crucial_data = self.plot_widget.stop_recording()
            self.export_to_excel(crucial_data, patient="Patient Name")

    def export_to_excel(self, crucial, patient):
        # Create a new Excel workbook and select the active sheet
        wb = openpyxl.Workbook()
        sheet = wb.active

        # Header row
        sheet.append(["Position", "Value"])

        # Data rows
        for position, value in enumerate(crucial):
            sheet.append([position, value])

        # Specify the full path where you want to save the Excel file
        file_path = r"D:\UDESC\TCC\Programas\GUIpreliminar\dados_do_paciente.xlsx"

        # Save the workbook to the specified file path
        wb.save(file_path)

        print(f"Data exported to Excel file: {file_path}")


class DataUpdater(QObject):
    data_updated = pyqtSignal(np.ndarray)
    print("debug 1")

    def __init__(self, parent=None):
        print("DataUpdater thread iniciada")
        super().__init__(parent)
        self.peak_value = 0
        self.peak_index = 0
        self.serial_port = "COM5"  # Selecione a porta correta
        self.data_buffer = np.zeros(250)
        self.recording = False
        self.data_buffer_lock = QMutex()

        try:
            self.arduino = serial.Serial(self.serial_port, 57600, timeout=1)
        except serial.SerialException as e:
            print(f"Erro ao abrir a porta serial: {e}")
            sys.exit(1)

        # Adicione um QTimer para atualizar a interface gráfica
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Atualizar a cada 100 ms

        # Thread para leitura dos dados
        self.thread = threading.Thread(target=self.read_serial_data)
        print("debug x")
        self.thread.start()

    def update_data(self):
        print("debug 2")
        self.data_updated.emit(self.data_buffer)

    def read_serial_data(self):
        try:
            print("Thread de leitura iniciada")
            while True:
                data_str = self.arduino.readline().decode('utf-8').strip()
                print(f"Recebido: {data_str}")

                if data_str:
                    try:
                        value = float(data_str)
                        print(f"Valor convertido: {value}")
                    except ValueError:
                        print(f"Erro ao converter '{data_str}' para float")

                    with self.data_buffer_lock:
                        self.data_buffer = np.roll(self.data_buffer, -1)
                        self.data_buffer[-1] = value

                    if value > self.peak_value:
                        print("Pico detectado")
                        self.peak_value = np.max(self.data_buffer)
                        self.peak_index = np.argmax(self.data_buffer)

        except serial.SerialException as e:
            print(f"Erro ao ler da porta serial: {e}")
        except KeyboardInterrupt:
            # Fechar a comunicação serial quando pressionar Ctrl+C
            self.arduino.close()
            print("Comunicação serial fechada.")

    def stop_recording(self):
        self.recording = False


class LivePlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self.data_buffer = np.zeros(100)
        self.data_buffer_lock = QMutex()  # Adicione o lock para acesso seguro ao data_buffer

        self.recording = False
        self.plot_line, = self.ax.plot([], [])

        # Adicione um QTimer para atualizar a interface gráfica
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_interface)
        self.timer.start(100)  # Atualizar a cada 100 ms

        self.ax.set_xlim(0, 100)  # Assuming 100 data points
        self.ax.set_ylim(0, 1024)

    def update_interface(self):
        with self.data_buffer_lock:
            x_values = np.arange(len(self.data_buffer))
            y_values = self.data_buffer.copy()  # Crie uma cópia para garantir consistência

        self.plot_line.set_data(x_values, y_values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def start_recording(self):
        self.recording = True

    def stop_recording(self):
        self.recording = False
        # Adicione o retorno dos dados cruciais
        return [np.max(self.data_buffer), np.mean(self.data_buffer), np.std(self.data_buffer)]

    def set_max_time(self, max_time_seconds):
        self.max_time_seconds = max_time_seconds


def main():
    try:
        app = QApplication(sys.argv)

        window = MainWindow()
        data_updater = DataUpdater()
        data_updater.data_updated.connect(window.plot_widget.update_interface)

        window.show()

        sys.exit(app.exec_())
    except Exception as e:
        print(f"Erro na execução: {e}")


if __name__ == "__main__":
    main()
