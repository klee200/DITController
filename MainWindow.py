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
        self.addRemoveWindow = AddRemoveSegmentWindow()
        self.copyWindow = CopySegmentWindow(self)
        self.calcWindow = CalculatorWindow(self)
        self.calibrateWindow = PlotCalibrateWindow(self)
        
        self.dataWindow = DataWindow(self.connectWindow.dataPort.dataThread.dataPlotTrigger)
        
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
        self.copyAction = self.editMenu.addAction("Copy segment")
        self.calcAction = self.editMenu.addAction("Calculator")
        self.calibrateAction = self.editMenu.addAction("Calibrate plot")
        
        self.settingsMenu = self.menuBar().addMenu("Settings")
        self.connectAction = self.settingsMenu.addAction("Connect")

    def build_window(self):
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QGridLayout())
        
        self.centralWidget().layout().setColumnStretch(0, 1)
        self.centralWidget().layout().setColumnStretch(1, 0)
        
        self.centralWidget().layout().addWidget(self.scanWidget, 0, 0, 2, 1)
        self.centralWidget().layout().addWidget(self.btnWidget, 0, 1)
        self.centralWidget().layout().addWidget(self.textWidget, 1, 1)

        # # Top right displays frequency and m/z options
        # self.conversion_layout = QGridLayout()
        # # Add layout to right half
        # self.rightLayout.addLayout(self.conversion_layout)
        # # Create buttons at locations (row, column) in grid
        # # Select frequency or m/z display
        # self.frequency_button = QRadioButton("Frequency")
        # self.conversion_layout.addWidget(self.frequency_button, 0, 0)
        # self.mass_button = QRadioButton("m/z")
        # self.conversion_layout.addWidget(self.mass_button, 0, 1)
        # self.convert_buttons = QButtonGroup()
        # self.convert_buttons.addButton(self.frequency_button)
        # self.convert_buttons.addButton(self.mass_button)
        # # Initial state
        # self.frequency_button.setChecked(True)
        # self.mass_button.setCheckable(False)
        # # Create label and box for conversion constant
        # self.conversion_layout.addWidget(QLabel("Drive constant"), 1, 0)
        # self.conv_const_box = QLineEdit()
        # self.conversion_layout.addWidget(self.conv_const_box, 1, 1)
        # self.conv_const_box.textChanged.connect(lambda: self.setConversionState(self.conv_const_box.text(), self.tickle_const_box.text()))
        # self.conversion_layout.addWidget(QLabel("Tickle constant"), 2, 0)
        # self.tickle_const_box = QLineEdit()
        # self.conversion_layout.addWidget(self.tickle_const_box, 2, 1)
        # self.tickle_const_box.textChanged.connect(lambda: self.setConversionState(self.conv_const_box.text(), self.tickle_const_box.text()))
        # # Number display select functions
        # self.frequency_button.toggled.connect(lambda: self.convertNumbers(self.conv_const_box.text(), self.tickle_const_box.text()))

        # Middle right displays buttons in grid layout
        # self.buttonLayout = QGridLayout()
        # Add button layout to right half
        # self.rightLayout.addLayout(self.buttonLayout)
        # Download button
        # self.downloadBtn = QPushButton("Download Scan")
        # self.buttonLayout.addWidget(self.downloadBtn, 4, 0)
        # Download button function
        # self.downloadBtn.clicked.connect(self.download_scan)
        # Upload button
        # self.uploadBtn = QPushButton("Upload Scan")
        # self.buttonLayout.addWidget(self.uploadBtn, 4, 1)
        # Upload button function
        # self.uploadBtn.clicked.connect(self.upload_scan)
        # Run button
        # self.runBtn = QPushButton("Run Scan")
        # self.buttonLayout.addWidget(self.runBtn, 5, 0)
        # Run button function
        # self.runBtn.clicked.connect(self.run_scan)
        # Stop button
        # self.stopBtn = QPushButton("Stop Scan")
        # self.buttonLayout.addWidget(self.stopBtn, 5, 1)
        # Stop button function
        # self.stopBtn.clicked.connect(self.stop_scan)
        # self.stopBtn.setEnabled(False)

    # def setConversionState(self, drive_constant, tickle_constant):
    #     try:
    #         # If constant box has a number allow user to push conversion buttons
    #         float(drive_constant)
    #         float(tickle_constant)
    #         self.frequency_button.setCheckable(True)
    #         self.mass_button.setCheckable(True)
    #     except:
    #         # Otherwise the user cannot push buttons (based on which is already pushed)
    #         if self.frequency_button.isChecked():
    #             self.mass_button.setCheckable(False)
    #         else:
    #             self.frequency_button.setCheckable(False)
    #
    # def convertNumbers(self, conversion_constant, tickle_constant):
    #     if self.frequency_button.isChecked() == True:
    #         self.scanFunction.convertToFrequency(conversion_constant, tickle_constant)
    #     elif self.mass_button.isChecked() == True:
    #         self.scanFunction.convertToMass(conversion_constant, tickle_constant)
    
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
            readInputList = self.connectWindow.controlPort.serial_read('Download finished')
            for readInput in readInputList:
                self.textWidget.appendPlainText(readInput)
        except SerialException:
            self.textChanged.appendPlainText("No serial port found")

    def upload_scan(self):
        try:
            self.connectWindow.controlPort.serial_write('U')
            readInputList = self.connectWindow.controlPort.serial_read('Upload finished')
            for readInput in readInputList:
                self.textWidget.appendPlainText(readInput)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def run_scan(self):
        self.connectWindow.dataPort.dataThread.controlPortAccess = True
        try:
            self.connectWindow.controlPort.serial_write('R')
            self.btnWidget.downloadBtn.setEnabled(False)
            self.btnWidget.uploadBtn.setEnabled(False)
            self.btnWidget.runBtn.setEnabled(False)
            self.btnWidget.stopBtn.setEnabled(True)
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def stop_scan(self):
        self.connectWindow.dataPort.dataThread.controlPortAccess = False
        try:
            sleep(1)
            self.connectWindow.controlPort.serial_write('S')
            self.connectWindow.controlPort.reset_input_buffer()
            self.btnWidget.downloadBtn.setEnabled(True)
            self.btnWidget.uploadBtn.setEnabled(True)
            self.btnWidget.runBtn.setEnabled(True)
            self.btnWidget.stopBtn.setEnabled(False)
        except SerialException:
            self.announcer.appendPlainText("No serial port found")


        
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
        