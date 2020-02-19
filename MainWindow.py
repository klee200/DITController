import pdb
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from DialogWindows import *
from DataWindow import *
from ScanFunction import *
from serial import *
from time import *


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.textWidget = TextWidget()
        self.scanWidget = ScanWidget(self.textWidget)
        self.btnWidget = BtnWidget()
        
        self.connectWindow = ConnectionWindow(self.textWidget)
        self.dataSettingsWindow = DataSettingsWindow()
        self.addRemoveWindow = AddRemoveSegmentWindow()
        self.calcWindow = CalculatorWindow()
        
        self.dataWindow = DataWindow()
        
        self.build_menu()
        self.build_window()
        
        self.showMaximized()
        
    def build_menu(self):
        self.menuBar()
        
        self.fileMenu = self.menuBar().addMenu("File")
        self.openAction = self.fileMenu.addAction("Open Scan")
        self.saveAction = self.fileMenu.addAction("Save Scan")
        
        self.editMenu = self.menuBar().addMenu("Edit")
        self.addRemoveAction = self.editMenu.addAction("Add/Remove segments")
        self.calcAction = self.editMenu.addAction("Calculator")
        self.calibrateAction = self.editMenu.addAction("Calibrate plot")
        
        self.settingsMenu = self.menuBar().addMenu("Settings")
        self.connectAction = self.settingsMenu.addAction("Connect")
        self.dataSettingsAction = self.settingsMenu.addAction("Data Settings")

    def build_window(self):
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QGridLayout())
        
        self.centralWidget().layout().setColumnStretch(0, 1)
        self.centralWidget().layout().setColumnStretch(1, 0)
        
        self.centralWidget().layout().addWidget(self.scanWidget, 0, 0, 2, 1)
        self.centralWidget().layout().addWidget(self.btnWidget, 0, 1)
        self.centralWidget().layout().addWidget(self.textWidget, 1, 1)
    
    def closeEvent(self, event):
        event.ignore()
        choice = self.scanWidget.save_check()
        if choice == QMessageBox.Cancel:
            pass
        else:
            if choice == QMessageBox.Yes:
                self.scanWidget.save_scan()
            sys.exit()
    
    def download_scan(self):
        try:
            scanData = json.dumps(self.scanWidget.scanFunction)
            self.connectWindow.controlPort.serial_write('D')
            self.connectWindow.controlPort.serial_write(scanData)
            # readInputList = self.connectWindow.controlPort.serial_read('Download finished')
            # for readInput in readInputList:
                # self.textWidget.appendPlainText(readInput)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def upload_scan(self):
        try:
            self.connectWindow.controlPort.serial_write('U')
            # readInputList = self.connectWindow.controlPort.serial_read('Upload finished')
            # for readInput in readInputList:
                # self.textWidget.appendPlainText(readInput)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def run_scan(self):
        # self.connectWindow.dataPort.dataThread.controlPortAccess = True
        try:
            self.connectWindow.controlPort.serial_write('R')
            self.btnWidget.downloadBtn.setEnabled(False)
            self.btnWidget.uploadBtn.setEnabled(False)
            self.btnWidget.runBtn.setEnabled(False)
            self.btnWidget.stopBtn.setEnabled(True)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def stop_scan(self):
        # self.connectWindow.dataPort.dataThread.controlPortAccess = False
        try:
            sleep(1)
            self.connectWindow.controlPort.serial_write('S')
            self.connectWindow.controlPort.reset_input_buffer()
            self.btnWidget.downloadBtn.setEnabled(True)
            self.btnWidget.uploadBtn.setEnabled(True)
            self.btnWidget.runBtn.setEnabled(True)
            self.btnWidget.stopBtn.setEnabled(False)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")
        
class BtnWidget(QWidget):
    def __init__(self):
        super(BtnWidget, self).__init__()
        
        self.downloadBtn = QPushButton("Download Scan")
        self.uploadBtn = QPushButton("Upload Scan")
        self.runBtn = QPushButton("Run Scan")
        self.stopBtn = QPushButton("Stop Scan")
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(self.downloadBtn, 0, 0)
        self.layout().addWidget(self.uploadBtn, 0, 1)
        self.layout().addWidget(self.runBtn, 1, 0)
        self.layout().addWidget(self.stopBtn, 1, 1)
        self.stopBtn.setEnabled(False)
        
class TextWidget(QPlainTextEdit):
    def __init__(self):
        super(TextWidget, self).__init__()
        
        self.setReadOnly(True)
        