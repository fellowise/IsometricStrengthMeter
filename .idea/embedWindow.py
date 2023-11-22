import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sine Wave Animation")

        # Create the main widget
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Create a vertical layout for the main widget
        layout = QVBoxLayout(main_widget)

        # Create a custom widget to host the Matplotlib plot
        self.plot_widget = PlotWidget()

        # Add the plot widget to the layout
        layout.addWidget(self.plot_widget)

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
        self.animation = FuncAnimation(self.figure, self.update_plot, interval=50)

        self.ax.set_xlim(0, 2 * np.pi)
        self.ax.set_ylim(-1.5, 1.5)

    def update_plot(self, frame):
        x = np.linspace(0, 2 * np.pi, 1000)
        y = np.sin(x + frame * 0.1)

        self.plot_line.set_data(x, y)
        self.canvas.draw()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
