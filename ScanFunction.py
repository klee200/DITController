from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pdb

WIDTH = 90
HEIGHT = 24
ANALOG_ROWS = 16
DIGITAL_ROWS = 21
ROWS = 7+16+21

class ScanFunction(object):
    def __init__(self):
        # Create header for scan function object
        self.header = ScanFunctionHeader()
        # Create list for holding segment objects
        self.scan_list = []

    def addSegment(self):
        # Add new segment object to list
        self.scan_list.append(ScanFunctionSegment())

    def removeSegment(self):
        # Remove segment object from list
        self.scan_list.pop()

class ScanFunctionHeader(QWidget):
    def __init__(self):
        super(ScanFunctionHeader, self).__init__()
        # Create header for Scan Function object
        self.header_layout = QVBoxLayout()
        self.setLayout(self.header_layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # Create labels
        self.name_label = QLabel('Name')
        self.header_layout.addWidget(self.name_label)
        self.type_label = QLabel("Type")
        self.header_layout.addWidget(self.type_label)
        self.duration_label = QLabel("Duration")
        self.header_layout.addWidget(self.duration_label)
        self.startfreq_label = QLabel("Start Frequency")
        self.header_layout.addWidget(self.startfreq_label)
        self.endfreq_label = QLabel("End Frequency")
        self.header_layout.addWidget(self.endfreq_label)
        self.dutycycle_label = QLabel("Duty Cycle")
        self.header_layout.addWidget(self.dutycycle_label)
        self.stepres_label = QLabel("Step Resolution")
        self.header_layout.addWidget(self.stepres_label)
        # Set up table of analog output labels
        self.analog_label = QTableWidget(ANALOG_ROWS, 1)
        self.analog_label.horizontalHeader().hide()
        self.analog_label.verticalHeader().hide()
        self.analog_label.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.analog_label.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.analog_label.setFixedSize(WIDTH, HEIGHT*ANALOG_ROWS+2)
        self.header_layout.addWidget(self.analog_label)
        # Set up table of digital output labels
        self.digital_label = QTableWidget(DIGITAL_ROWS, 1)
        self.digital_label.horizontalHeader().hide()
        self.digital_label.verticalHeader().hide()
        self.digital_label.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.digital_label.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.digital_label.setFixedSize(WIDTH, HEIGHT*DIGITAL_ROWS+2)
        self.header_layout.addWidget(self.digital_label)

class ScanFunctionSegment(QWidget):
    def __init__(self):
        super(ScanFunctionSegment, self).__init__()
        # Create layout for segment
        self.segment_layout = QVBoxLayout()
        self.setLayout(self.segment_layout)
        self.setFixedWidth(200)

        # Create table for parameters
        self.segment_table = QTableWidget(7, 2)
        # Add table to layout
        self.segment_layout.addWidget(self.segment_table)
        # Set up sizes and hide default headers
        self.segment_table.horizontalHeader().hide()
        self.segment_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.segment_table.verticalHeader().hide()
        self.segment_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.segment_table.setFixedHeight(HEIGHT*7+2)
        # Set up labels
        self.segment_table.setItem(0, 0, QTableWidgetItem("Name"))
        self.segment_table.setItem(1, 0, QTableWidgetItem("Type"))
        self.segment_table.setItem(2, 0, QTableWidgetItem("Duration"))
        self.segment_table.setItem(3, 0, QTableWidgetItem("Start Freq"))
        self.segment_table.setItem(4, 0, QTableWidgetItem("End Freq"))
        self.segment_table.setItem(5, 0, QTableWidgetItem("Duty Cycle"))
        self.segment_table.setItem(6, 0, QTableWidgetItem("Step Res"))
        # Set up type option box
        self.type_box = QComboBox()
        self.type_box.addItem("Fixed")
        self.type_box.addItem("Ramp")
        self.type_box.addItem("Mass Analysis")
        self.type_box.addItem("Dump")
        self.type_box.addItem("Custom")
        self.segment_table.setCellWidget(1, 1, self.type_box)

        # Create table for analog outputs
        self.analog_table = QTableWidget(ANALOG_ROWS, 2)
        # Add table to layout
        self.segment_layout.addWidget(self.analog_table)
        # Set up sizes and hide default headers
        self.analog_table.horizontalHeader().hide()
        self.analog_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.analog_table.verticalHeader().hide()
        self.analog_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.analog_table.setFixedHeight(HEIGHT*ANALOG_ROWS+2)
        # Set up labels
        for row in range(ANALOG_ROWS):
            self.analog_table.setItem(row, 0, QTableWidgetItem("A" + str(row+1)))

        # Create table for digital outputs
        self.digital_table = QTableWidget(DIGITAL_ROWS, 2)
        # Add table to layout
        self.segment_layout.addWidget(self.digital_table)
        # Set up sizes and hide default headers
        self.digital_table.horizontalHeader().hide()
        self.digital_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.digital_table.verticalHeader().hide()
        self.digital_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.digital_table.setFixedHeight(HEIGHT*DIGITAL_ROWS+2)
        # Set up labels
        for row in range(0, DIGITAL_ROWS):
            self.digital_table.setItem(row, 0, QTableWidgetItem("D" + str(row+1)))

        # Signal character for Arduino - default is 'f' for Fixed
        self.type = 'f'
