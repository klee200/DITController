from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from SerialPorts import *
from math import *
import numpy as np

class ConnectionWindow(QDialog):
    def __init__(self, textWidget):
        super(ConnectionWindow, self).__init__()
        self.textWidget = textWidget
        
        self.controlPort = ControlPort()
        self.dataPort = DataPort(self.controlPort)
        
        self.build_window()

    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Control"), 0, 0)
        self.controlBox = QLineEdit("COM6")
        self.layout().addWidget(self.controlBox, 0, 1)
        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.layout().addWidget(self.line, 2, 0, 1, 2)
        
        self.layout().addWidget(QLabel("Data"), 3, 0)
        self.dataBox = QLineEdit("COM7")
        self.layout().addWidget(self.dataBox, 3, 1)
        
        self.controlConnectBtn = QPushButton('Connect Controller')
        self.layout().addWidget(self.controlConnectBtn, 1, 0)
        self.controlDisconnectBtn = QPushButton('Disconnect Controller')
        self.layout().addWidget(self.controlDisconnectBtn, 1, 1)
        self.dataConnectBtn = QPushButton('Connect Data')
        self.layout().addWidget(self.dataConnectBtn, 4, 0)
        self.dataDisconnectBtn = QPushButton('Disconnect Data')
        self.layout().addWidget(self.dataDisconnectBtn, 4, 1)

    def connect_control(self):
        try:
            self.controlPort.port = self.controlBox.text()
            self.controlPort.open()
            self.textWidget.appendPlainText("Controller connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def disconnect_control(self):
        try:
            self.controlPort.close()
            self.textWidget.appendPlainText("Controller disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")
        
    def connect_data(self):
        try:
            self.dataPort.port = self.dataBox.text()
            self.dataPort.open()
            self.dataPort.dataThread.start()
            self.textWidget.appendPlainText("Data serial connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")
        
    def disconnect_data(self):
        try:
            self.dataPort.close()
            self.textWidget.appendPlainText("Data serial disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")


class AddRemoveSegmentWindow(QDialog):
    def __init__(self):
        super(AddRemoveSegmentWindow, self).__init__()
        self.build_window()
        
    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Insert new segment at position:"), 1, 0)
        self.addPositionBox = QLineEdit("1")
        self.layout().addWidget(self.addPositionBox, 1, 1)
        self.layout().addWidget(QLabel("Remove segment from position:"), 3, 0)
        self.removePositionBox = QLineEdit("1")
        self.layout().addWidget(self.removePositionBox, 3, 1)
        
        self.addSegBtn = QPushButton("Insert segment")
        self.layout().addWidget(self.addSegBtn, 2, 0, 1, 2)
        self.removeSegBtn = QPushButton("Remove segment")
        self.layout().addWidget(self.removeSegBtn, 4, 0, 1, 2)

class CalculatorWindow(QDialog):
    updated = pyqtSignal(object)

    def __init__(self):
        super(CalculatorWindow, self).__init__()
        
        self.constant = 0
        
        self.ELECTRON = 1.602e-19
        self.AMU = 1.66e-27
        self.rBox = QLineEdit("0.707")
        self.zBox = QLineEdit("0.774")
        self.hvBox = QLineEdit("200")
        self.lvBox = QLineEdit("-200")
        self.dBox = QLineEdit("50")
        self.freqBtn = QPushButton("Frequency")
        self.freqBox = QLineEdit("200000")
        self.mzBtn = QPushButton("m/z")
        self.mzBox = QLineEdit("2000")
        self.targetBox = QLineEdit("1")
        self.brBox = QLineEdit()
        self.bzBox = QLineEdit()
        self.orBox = QLineEdit()
        self.ozBox = QLineEdit()
        
        self.build_window()
        self.signal_handler()
        
    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("r\u2080 (cm)"), 0, 0)
        self.layout().addWidget(self.rBox, 0, 1)
        self.layout().addWidget(QLabel("z\u2080 (cm)"), 1, 0)
        self.layout().addWidget(self.zBox, 1, 1)
        
        self.layout().addWidget(QLabel("High V (V)"), 0, 2)
        self.layout().addWidget(self.hvBox, 0, 3)
        self.layout().addWidget(QLabel("Low V (V)"), 1, 2)
        self.layout().addWidget(self.lvBox, 1, 3)
        self.layout().addWidget(QLabel("Duty Cycle (%)"), 2, 2)
        self.layout().addWidget(self.dBox, 2, 3)
        
        self.layout().addWidget(self.freqBtn, 0, 4)
        self.layout().addWidget(self.freqBox, 0, 5)
        self.layout().addWidget(self.mzBtn, 1, 4)
        self.layout().addWidget(self.mzBox, 1, 5)
        
        self.layout().addWidget(QLabel("Target Beta z"), 2, 4)
        self.layout().addWidget(self.targetBox, 2, 5)
        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.layout().addWidget(self.line, 3, 0, 1, 6)
                
        self.layout().addWidget(QLabel("Beta r"), 4, 2)
        self.layout().addWidget(self.brBox, 4, 3)
        self.brBox.setEnabled(False)
        self.layout().addWidget(QLabel("Beta z"), 4, 4)
        self.layout().addWidget(self.bzBox, 4, 5)
        self.bzBox.setEnabled(False)
        self.layout().addWidget(QLabel("omega r (Hz)"), 5, 2)
        self.layout().addWidget(self.orBox, 5, 3)
        self.orBox.setEnabled(False)
        self.layout().addWidget(QLabel("omega z (Hz)"), 5, 4)
        self.layout().addWidget(self.ozBox, 5, 5)
        self.ozBox.setEnabled(False)

    def signal_handler(self):
        self.rBox.textChanged.connect(self.update)
        self.zBox.textChanged.connect(self.update)
        self.hvBox.textChanged.connect(self.update)
        self.lvBox.textChanged.connect(self.update)
        self.dBox.textChanged.connect(self.update)
        self.freqBox.textChanged.connect(self.update)
        self.mzBox.textChanged.connect(self.update)
        
        self.freqBtn.clicked.connect(self.calc_freq)
        self.mzBtn.clicked.connect(self.calc_mz)
        
        self.update()
        self.calc_freq()

    def update(self):
        self.targetBox.setText(str(max(min(float(self.targetBox.text()), 1), 0)))
        
        self.calc_beta_r()
        self.calc_beta_z()
        self.calc_omega_r()
        self.calc_omega_z()
        
        self.constant = float(self.freqBox.text())**2 * float(self.mzBox.text())
        self.updated.emit(str(self.constant))

    def calc_beta_r(self):
        try:
            dHi = float(self.dBox.text()) / 100 * pi
            dLo = (1 - float(self.dBox.text()) / 100) * pi

            frHi = 2 * 4 * self.ELECTRON * float(self.hvBox.text()) / (float(self.mzBox.text()) * self.AMU * pow(float(self.freqBox.text()) * 2 * pi, 2) * (pow(float(self.rBox.text()) / 100, 2) + 2* pow(float(self.zBox.text()) / 100, 2)))
            mrHi = [[0 for x in range(2)] for y in range(2)]
            if frHi > 0:
                mrHi[0][0] = cos(sqrt(frHi) * dHi)
                mrHi[0][1] = 1 / sqrt(frHi) * sin(sqrt(frHi) * dHi)
                mrHi[1][0] = -sqrt(frHi) * sin(sqrt(frHi) * dHi)
                mrHi[1][1] = cos(sqrt(frHi) * dHi)
            else:
                mrHi[0][0] = cosh(sqrt(-frHi) * dHi)
                mrHi[0][1] = 1 / sqrt(-frHi) * sinh(sqrt(-frHi) * dHi)
                mrHi[1][0] = sqrt(-frHi) * sinh(sqrt(-frHi) * dHi)
                mrHi[1][1] = cosh(sqrt(-frHi) * dHi)

            frLo = 2 * 4 * self.ELECTRON * float(self.lvBox.text()) / (float(self.mzBox.text()) * self.AMU * pow(float(self.freqBox.text()) * 2 * pi, 2) * (pow(float(self.rBox.text()) / 100, 2) + 2 * pow(float(self.zBox.text()) / 100, 2)))
            mrLo = [[0 for x in range(2)] for y in range(2)]
            if frLo > 0:
                mrLo[0][0] = cos(sqrt(frLo) * dLo)
                mrLo[0][1] = 1 / sqrt(frLo) * sin(sqrt(frLo) * dLo)
                mrLo[1][0] = -sqrt(frLo) * sin(sqrt(frLo) * dLo)
                mrLo[1][1] = cos(sqrt(frLo) * dLo)
            else:
                mrLo[0][0] = cosh(sqrt(-frLo) * dLo)
                mrLo[0][1] = 1 / sqrt(-frLo) * sinh(sqrt(-frLo) * dLo)
                mrLo[1][0] = sqrt(-frLo) * sinh(sqrt(-frLo) * dLo)
                mrLo[1][1] = cosh(sqrt(-frLo) * dLo)
            mr = np.dot(mrHi, mrLo)
            betaR = acos((mr[0][0] + mr[1][1]) / 2) / pi
            
        except:
            betaR = inf
            
        self.brBox.setText(str(betaR))

    def calc_beta_z(self):
        try:
            dHi = float(self.dBox.text()) / 100 * pi
            dLo = (1 - float(self.dBox.text()) / 100) * pi

            fzHi = -2 * 8 * self.ELECTRON * float(self.hvBox.text()) / (float(self.mzBox.text()) * self.AMU * pow(float(self.freqBox.text()) * 2 * pi, 2) * (pow(float(self.rBox.text()) / 100, 2) + 2 * pow(float(self.zBox.text()) / 100, 2)))
            mzHi = [[0 for x in range(2)] for y in range(2)]
            if fzHi > 0:
                mzHi[0][0] = cos(sqrt(fzHi) * dHi)
                mzHi[0][1] = 1 / sqrt(fzHi) * sin(sqrt(fzHi) * dHi)
                mzHi[1][0] = -sqrt(fzHi) * sin(sqrt(fzHi) * dHi)
                mzHi[1][1] = cos(sqrt(fzHi) * dHi)
            else:
                mzHi[0][0] = cosh(sqrt(-fzHi) * dHi)
                mzHi[0][1] = 1 / sqrt(-fzHi) * sinh(sqrt(-fzHi) * dHi)
                mzHi[1][0] = sqrt(-fzHi) * sinh(sqrt(-fzHi) * dHi)
                mzHi[1][1] = cosh(sqrt(-fzHi) * dHi)

            fzLo = -2 * 8 * self.ELECTRON * float(self.lvBox.text()) / (float(self.mzBox.text()) * self.AMU * pow(float(self.freqBox.text()) * 2 * pi, 2) * (pow(float(self.rBox.text()) / 100, 2) + 2 * pow(float(self.zBox.text()) / 100, 2)))
            mzLo = [[0 for x in range(2)] for y in range(2)]
            if fzLo > 0:
                mzLo[0][0] = cos(sqrt(fzLo) * dLo)
                mzLo[0][1] = 1 / sqrt(fzLo) * sin(sqrt(fzLo) * dLo)
                mzLo[1][0] = -sqrt(fzLo) * sin(sqrt(fzLo) * dLo)
                mzLo[1][1] = cos(sqrt(fzLo) * dLo)
            else:
                mzLo[0][0] = cosh(sqrt(-fzLo) * dLo)
                mzLo[0][1] = 1 / sqrt(-fzLo) * sinh(sqrt(-fzLo) * dLo)
                mzLo[1][0] = sqrt(-fzLo) * sinh(sqrt(-fzLo) * dLo)
                mzLo[1][1] = cosh(sqrt(-fzLo) * dLo)
            mz = np.dot(mzHi, mzLo)
            betaZ = acos((mz[0][0] + mz[1][1]) / 2) / pi
            
        except:
            betaZ = inf
            
        self.bzBox.setText(str(betaZ))

    def calc_omega_r(self):
        try:
            omegaR = 1 / 2 * float(self.brBox.text()) * float(self.freqBox.text())
            
        except:
            omegaR = None

        self.orBox.setText(str(omegaR))
        
    def calc_omega_z(self):
        try:
            omegaZ = 1 / 2 * float(self.bzBox.text()) * float(self.freqBox.text())
            
        except:
            omegaZ = None
            
        self.ozBox.setText(str(omegaZ))

    def calc_freq(self):
        for i in range(floor(log10(float(self.freqBox.text()))), -1, -1):
            if float(self.brBox.text()) == inf or float(self.bzBox.text()) == inf:
                None
            elif float(self.bzBox.text()) < float(self.targetBox.text()):
                while float(self.bzBox.text()) < float(self.targetBox.text()) and float(self.brBox.text()) < inf and float(self.freqBox.text()) > 0:
                    self.freqBox.setText(str(float(self.freqBox.text()) - pow(10, i)))
                self.freqBox.setText(str(float(self.freqBox.text()) + pow(10, i)))
            else:
                while float(self.bzBox.text()) > float(self.targetBox.text()) and float(self.bzBox.text()) < inf and float(self.brBox.text()) < inf and float(self.freqBox.text()) > 0:
                    self.freqBox.setText(str(float(self.freqBox.text()) + pow(10, i)))
                self.freqBox.setText(str(float(self.freqBox.text()) - pow(10, i)))
                
    def calc_mz(self):
        for i in range(floor(log10(float(self.mzBox.text()))), -1, -1):
            if float(self.brBox.text()) == inf or float(self.bzBox.text()) == inf:
                None
            elif float(self.bzBox.text()) < float(self.targetBox.text()):
                while float(self.bzBox.text()) < float(self.targetBox.text()) and float(self.brBox.text()) < inf and float(self.mzBox.text()) > 0:
                    self.mzBox.setText(str(float(self.mzBox.text()) - pow(10, i)))
                self.mzBox.setText(str(float(self.mzBox.text()) + pow(10, i)))
            else:
                while float(self.bzBox.text()) > float(self.targetBox.text()) and float(self.bzBox.text()) < inf and float(self.brBox.text()) < inf and float(self.mzBox.text()) > 0:
                    self.mzBox.setText(str(float(self.mzBox.text()) + pow(10, i)))
                self.mzBox.setText(str(float(self.mzBox.text()) - pow(10, i)))

class CalibrateWindow(QDialog):
    def __init__(self):
        super(CalibrateWindow, self).__init__()
        
        self.values = range(0, 100)
        
        self.build_window()
        
    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.table = QTableWidget(2, 2)
        self.layout().addWidget(self.table)
        self.table.setHorizontalHeaderLabels(['points', 'frequency'])
        self.table.setVerticalHeaderLabels(['start', 'end'])
        
        self.values = range(0, 100)
        
    def update(self):
        self.values = range(constant / values[0]**2, constant / values[1]**2, round((constant / values[1]**2 - constant / values[0]**2) / length))

                
class PlotCalibrateWindow(QDialog):
    def __init__(self, mainWindow):
        super(PlotCalibrateWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # Make layout
        self.setLayout(QHBoxLayout())
        # Add table to layout
        self.NUM_ROWS = 5
        self.NUM_COLS = 2
        self.peak_table = QTableWidget(self.NUM_ROWS, self.NUM_COLS)
        # self.peak_table.setFixedHeight(HEIGHT * (self.NUM_ROWS + 1) + 2)
        # self.peak_table.setFixedWidth(WIDTH * self.NUM_COLS + 2)
        # self.peak_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.peak_table.verticalHeader().hide()
        # self.peak_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.peak_table.setHorizontalHeaderLabels(['x', 'm/z'])
        self.layout().addWidget(self.peak_table)
        # Connect table to value update
        for i in range(self.NUM_ROWS):
            for j in range(self.NUM_COLS):
                self.peak_table.setItem(i, j, QTableWidgetItem())
        self.peak_table.itemChanged.connect(self.update)
        # Add parameter layout to layout
        self.parameter_layout = QGridLayout()
        self.layout().addLayout(self.parameter_layout)
        # Add slope parameter to layout
        self.parameter_layout.addWidget(QLabel("Slope"), 0, 0)
        self.slope_box = QLineEdit()
        self.slope_box.setEnabled(False)
        self.parameter_layout.addWidget(self.slope_box, 0, 1)
        # Add intercept parameter to layout
        self.parameter_layout.addWidget(QLabel("Intercept"), 1, 0)
        self.intercept_box = QLineEdit()
        self.intercept_box.setEnabled(False)
        self.parameter_layout.addWidget(self.intercept_box, 1, 1)
        # Add R^2 result to layout
        self.parameter_layout.addWidget(QLabel("R^2"), 2, 0)
        self.r_2_box = QLineEdit()
        self.r_2_box.setEnabled(False)
        self.parameter_layout.addWidget(self.r_2_box, 2, 1)
        
    def update(self):
        x = []
        y = []
        for i in range(self.NUM_ROWS):
            try:
                x.append(float(self.peak_table.item(i, 0).text()))
                y.append(float(self.peak_table.item(i, 1).text()))
            except:
                None
        self.calculateSlope(x, y)
        self.calculateIntercept(x, y)
        self.calculateR2(x, y)
        
    def calculateIntercept(self, x, y):
        try:
            intercept = (sum(y) * sum([i**2 for i in x]) - sum(x) * sum([i * j for i, j in zip(x, y)])) / (len(x) * sum([i**2 for i in x]) - sum(x)**2)
        except:
            intercept = None
        self.intercept_box.setText(str(intercept))
        
    def calculateSlope(self, x, y):
        try:
            slope = (len(x) * sum([i * j for i, j in zip(x, y)]) - sum(x) * sum(y)) / (len(x) * sum([i**2 for i in x]) - sum(x)**2)
        except:
            slope = None
        self.slope_box.setText(str(slope))
        
    def calculateR2(self, x, y):
        try:
            res = sum([(i - j)**2 for i, j in zip(y, [float(self.slope_box.text()) * i + float(self.intercept_box.text()) for i in x])])
            tot = sum([(i - sum(y)/len(y))**2 for i in y])
            r2 = 1 - res / tot
        except:
            r2 = None
        self.r_2_box.setText(str(r2))