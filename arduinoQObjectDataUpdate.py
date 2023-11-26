import sys
import serial
import threading
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject


class DataUpdater(QObject):
    data_updated = pyqtSignal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.peak_value = 0
        self.peak_index = 0
        self.serial_port = "COM5"   # Selecione a porta correta
        self.data_buffer = np.zeros(250)
        self.recording = False

        try:
            self.arduino = serial.Serial(self.serial_port, 57600, timeout=1)
        except serial.SerialException as e:
            print(f"Erro ao abrir a porta serial: {e}")
            sys.exit(1)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_data)
        self.timer.start(100)  # Atualizar a cada 100 ms

        # Thread para leitura dos dados
        self.thread = threading.Thread(target=self.read_serial_data)
        self.thread.start()

    def update_data(self):
        self.data_updated.emit(self.data_buffer)

    def read_serial_data(self):
        try:
            while True:
                data_str = self.arduino.readline().decode('utf-8').strip()

                if data_str:
                    try:
                        value = float(data_str)
                    except ValueError:
                        print(f"Erro ao converter '{data_str}' para float")

                    self.data_buffer = np.roll(self.data_buffer, -1)
                    self.data_buffer[-1] = value

                    if value > self.peak_value:
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

class LivePlotWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.data_buffer = np.zeros(250)

    def update_plot(self, data_buffer):
        self.data_buffer = data_buffer
        self.scene.clear()

        x_values = np.arange(len(self.data_buffer))
        y_values = self.data_buffer

        for i in range(1, len(x_values)):
            line = self.scene.addLine(x_values[i - 1], y_values[i - 1], x_values[i], y_values[i])
            line.setPen(Qt.blue)


def main():
    app = QApplication(sys.argv)

    window = QMainWindow()
    window.setWindowTitle("Live Plot Example")
    window.setGeometry(100, 100, 800, 600)

    plot_widget = LivePlotWidget(window)
    window.setCentralWidget(plot_widget)

    data_updater = DataUpdater()
    data_updater.data_updated.connect(plot_widget.update_plot)

    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
