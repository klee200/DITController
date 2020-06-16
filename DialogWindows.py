from PyQt5.QtWidgets import QDialog, QGridLayout, QLabel, QLineEdit, QFrame, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from SerialPorts import ControlPort, DataPort, DataThread
from serial import SerialException
from math import pi, cos, sin, sqrt, cosh, sinh, acos, inf, floor, log10
import numpy as np

class ConnectionWindow(QDialog):
    def __init__(self, textWidget):
        super(ConnectionWindow, self).__init__()
        self.textWidget = textWidget
        
        self.controlPort = ControlPort()
        self.dataPort = DataPort(self.controlPort)
        self.dataThread = DataThread(self.controlPort, self.dataPort)
        
        self.build_window()
        
        self.signal_handler()

    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Control"), 0, 0)
        self.controlBox = QLineEdit("COM10")
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
        
    def signal_handler(self):
        self.controlConnectBtn.clicked.connect(self.connect_control)
        self.controlDisconnectBtn.clicked.connect(self.disconnect_control)
        self.dataConnectBtn.clicked.connect(self.connect_data)
        self.dataDisconnectBtn.clicked.connect(self.disconnect_data)

    def connect_control(self):
        try:
            self.controlPort.port = self.controlBox.text()
            self.controlPort.open()
            self.dataThread.controlPortAccess = True
            self.dataThread.start()
            self.textWidget.appendPlainText("Controller connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def disconnect_control(self):
        try:
            self.dataThread.controlPortAccess = False
            self.controlPort.close()
            self.textWidget.appendPlainText("Controller disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")
        
    def connect_data(self):
        try:
            self.dataPort.port = self.dataBox.text()
            self.dataPort.open()
            self.dataThread.dataPortAccess = True
            self.textWidget.appendPlainText("Data serial connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")
        
    def disconnect_data(self):
        try:
            self.dataThread.dataPortAccess = False
            self.dataPort.close()
            self.textWidget.appendPlainText("Data serial disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")

class DataSettingsWindow(QDialog):
    def __init__(self):
        super(DataSettingsWindow, self).__init__()
        self.build_window()
        
    def build_window(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Data point sampling:"), 0, 0)
        self.dataSampleBox = QLineEdit("4")
        self.layout().addWidget(self.dataSampleBox, 0, 1)
        
        self.applyBtn = QPushButton("Apply")
        self.layout().addWidget(self.applyBtn, 1, 0)

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
        self.hvBox = QLineEdit("400")
        self.lvBox = QLineEdit("-400")
        self.dBox = QLineEdit("50")
        self.freqBtn = QPushButton("Frequency")
        self.freqBox = QLineEdit("200000")
        self.mzBtn = QPushButton("m/z")
        self.mzBox = QLineEdit("2000")
        self.targetBox = QLineEdit("0.5")
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
