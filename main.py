from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
import sys


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        xposition = 100
        yposition = 100
        width = 640
        height = 480
        self.setGeometry(xposition, yposition, width, height)
        self.setWindowTitle("Medidor de Força Isométrica")
        self.initUI()


    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Primeiro texto")
        self.label.move(50, 50)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Aperte")
        self.b1.clicked.connect(self.clicked)

    def clicked(self):
        self.label.setText("Está apertado, certo")
        self.update()

    def update(self):
        self.label.adjustSize()

def window():
    app = QApplication(sys.argv)
    win = MyWindow()

    win.show()
    sys.exit(app.exec_())


window()