import sys
import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import QTimer


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        print("sim")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButtonCalibration = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonCalibration.setGeometry(QtCore.QRect(10, 170, 101, 24))
        self.pushButtonCalibration.setObjectName("pushButtonCalibration")
        self.graphicsView = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView.setGeometry(QtCore.QRect(310, 40, 441, 192))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = QtWidgets.QGraphicsView(self.centralwidget)
        self.graphicsView_2.setGeometry(QtCore.QRect(310, 290, 441, 192))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.labelTests = QtWidgets.QLabel(self.centralwidget)
        self.labelTests.setGeometry(QtCore.QRect(860, 40, 71, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.labelTests.setFont(font)
        self.labelTests.setObjectName("labelTests")
        self.pushButtonStart = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonStart.setGeometry(QtCore.QRect(10, 340, 101, 24))
        self.pushButtonStart.setObjectName("pushButtonStart")
        # error popup test
        self.pushButtonError = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonError.setGeometry(QtCore.QRect(850, 80, 101, 24))
        self.pushButtonError.setObjectName("pushButtonError")

        self.labelCalibration = QtWidgets.QLabel(self.centralwidget)
        self.labelCalibration.setGeometry(QtCore.QRect(150, 150, 101, 16))
        self.labelCalibration.setObjectName("labelCalibration")
        self.labelSetup = QtWidgets.QLabel(self.centralwidget)
        self.labelSetup.setGeometry(QtCore.QRect(190, 10, 49, 16))
        self.labelSetup.setObjectName("labelSetup")
        self.pushButtonSettings = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonSettings.setGeometry(QtCore.QRect(10, 30, 101, 24))
        self.pushButtonSettings.setObjectName("pushButtonSettings")
        self.labelPlaceHolder1 = QtWidgets.QLabel(self.centralwidget)
        self.labelPlaceHolder1.setGeometry(QtCore.QRect(310, 40, 441, 191))
        self.labelPlaceHolder1.setText("Press Calibration")
        # self.labelPlaceHolder1.setPixmap(QtGui.QPixmap("ImagemModelo1.png"))
        self.labelPlaceHolder1.setScaledContents(True)
        self.labelPlaceHolder1.setObjectName("labelPlaceHolder1")
        self.labelPlaceHolder2 = QtWidgets.QLabel(self.centralwidget)
        self.labelPlaceHolder2.setGeometry(QtCore.QRect(310, 290, 441, 201))
        self.labelPlaceHolder2.setText("Press Start")
        # self.labelPlaceHolder2.setPixmap(QtGui.QPixmap("ImagemModelo2.png"))
        self.labelPlaceHolder2.setScaledContents(True)
        self.labelPlaceHolder2.setObjectName("labelPlaceHolder2")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1001, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuNew = QtWidgets.QMenu(self.menuFile)
        self.menuNew.setObjectName("menuNew")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionPatient = QtWidgets.QAction(MainWindow)
        self.actionPatient.setObjectName("actionPatient")
        self.actionMeasure = QtWidgets.QAction(MainWindow)
        self.actionMeasure.setObjectName("actionMeasure")
        self.actionSave = QtWidgets.QAction(MainWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSaveAs = QtWidgets.QAction(MainWindow)
        self.actionSaveAs.setObjectName("actionSaveAs")
        self.actionCopy = QtWidgets.QAction(MainWindow)
        self.actionCopy.setObjectName("actionCopy")
        self.actionImport = QtWidgets.QAction(MainWindow)
        self.actionImport.setObjectName("actionImport")
        self.actionExport = QtWidgets.QAction(MainWindow)
        self.actionExport.setObjectName("actionExport")
        self.menuNew.addAction(self.actionPatient)
        self.menuNew.addAction(self.actionMeasure)
        self.menuFile.addAction(self.menuNew.menuAction())
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSaveAs)
        self.menuFile.addAction(self.actionImport)
        self.menuFile.addAction(self.actionExport)
        self.menuEdit.addAction(self.actionCopy)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.actionPatient.triggered.connect(lambda: self.clicked("New Pacient"))
        self.actionMeasure.triggered.connect(lambda: self.clicked("New Measure"))
        self.actionSave.triggered.connect(lambda: self.clicked("Save"))
        self.actionSaveAs.triggered.connect(lambda: self.clicked("Save As..."))
        self.actionImport.triggered.connect(lambda: self.clicked("Import"))
        self.actionExport.triggered.connect(lambda: self.clicked("Export"))
        self.actionCopy.triggered.connect(lambda: self.clicked("Copy"))

        self.pushButtonCalibration.clicked.connect(self.press_calibration)
        self.pushButtonStart.clicked.connect(self.press_start)
        self.pushButtonError.clicked.connect(self.error_popup)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButtonCalibration.setText(_translate("MainWindow", "Calibration"))
        self.labelTests.setText(_translate("MainWindow", "Test"))
        self.pushButtonStart.setText(_translate("MainWindow", "Start"))
        self.pushButtonError.setText(_translate("MainWindow", "Error"))
        self.labelCalibration.setText(_translate("MainWindow", "Calibration Values"))
        self.labelSetup.setText(_translate("MainWindow", "Setup"))
        self.pushButtonSettings.setText(_translate("MainWindow", "Settings"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuNew.setTitle(_translate("MainWindow", "New"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.actionPatient.setText(_translate("MainWindow", "Patient"))
        self.actionPatient.setStatusTip(_translate("MainWindow", "Create a new patient file"))
        self.actionPatient.setShortcut(_translate("MainWindow", "Ctrl+N"))
        self.actionMeasure.setText(_translate("MainWindow", "Measure"))
        self.actionMeasure.setStatusTip(_translate("MainWindow", "Create another measure"))
        self.actionMeasure.setShortcut(_translate("MainWindow", "Ctrl+Shift+N"))
        self.actionSave.setText(_translate("MainWindow", "Save"))
        self.actionSave.setShortcut(_translate("MainWindow", "Ctrl+S"))
        self.actionSaveAs.setText(_translate("MainWindow", "Save As..."))
        self.actionSaveAs.setShortcut(_translate("MainWindow", "Ctrl+Shift+S"))
        self.actionCopy.setText(_translate("MainWindow", "Copy"))
        self.actionImport.setText(_translate("MainWindow", "Import"))
        self.actionImport.setShortcut(_translate("MainWindow", "Ctrl+I"))
        self.actionExport.setText(_translate("MainWindow", "Export"))

    def clicked(self, text):
        self.labelTests.setText(text)
        self.labelTests.adjustSize()

    def press_calibration(self):
        self.labelPlaceHolder1.setPixmap(QtGui.QPixmap("ImagemModelo1.png"))


    def press_start(self):
        self.labelPlaceHolder2.setPixmap(QtGui.QPixmap("ImagemModelo2.png"))

    def error_popup(self):
        errorpopup = QMessageBox()
        errorpopup.setWindowTitle("Error Test")
        errorpopup.setText("Verify Arduino connection, or something")
        errorpopup.setIcon(QMessageBox.Question)
        errorpopup.setStandardButtons(QMessageBox.Retry|QMessageBox.Cancel)
        errorpopup.setInformativeText("Maybe you should try to fix our Arduino connection")
        errorpopup.buttonClicked(self.error_buttons)
        aux = errorpopup.exec_()

    def error_buttons(self, i):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino Signal Animation")

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
        self.animation = FuncAnimation(self.figure, self.update_plot, blit=True, interval=50)

        self.ax.set_xlim(0, 100)  # Assuming 100 data points
        self.ax.set_ylim(0, 1024)  # Assuming analog values range from 0 to 1023

        self.serial_port = "COM5"
        # Create a Serial object to communicate with Arduino
        self.arduino = serial.Serial(self.serial_port, 9600, timeout=1)
        # time.sleep(2)  # Removed, but may be necessary depending on your Arduino's behavior
        self.data_buffer = np.zeros(100)

        # QTimer to update Arduino data
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_arduino_data)
        self.timer.start(50)  # Update data every 50 ms

    def update_arduino_data(self):
        try:
            # Read value from pin A2 directly
            value = int(self.arduino.readline().decode('utf-8').strip())
            # Display the read value from pin A2
            print(f"Value from pin A2: {value}")

            # Update the data buffer
            self.data_buffer = np.roll(self.data_buffer, -1)
            self.data_buffer[-1] = value

        except KeyboardInterrupt:
            # Close the serial communication when pressing Ctrl+C
            self.arduino.close()
            print("Serial communication closed.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def update_plot(self, frame):
        x = np.arange(len(self.data_buffer))
        y = self.data_buffer

        self.plot_line.set_data(x, y)
        return self.plot_line,

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
