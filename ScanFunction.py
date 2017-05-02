from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import pdb

WIDTH = 90
HEIGHT = 24
ANALOG_ROWS = 16
DIGITAL_ROWS = 21
PARAMETER_ROWS = 6
ROWS = ANALOG_ROWS + DIGITAL_ROWS + PARAMETER_ROWS

class ScanFunction(object):
    def __init__(self):
        # Create header for scan function object
        # self.header = ScanFunctionHeader()
        # Create list for holding segment objects
        self.scan_list = []
        # Create updating plot object
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.scan_plot = ScanFunctionPlot()

    def addSegment(self):
        # Add new segment object to list
        self.scan_list.append(ScanFunctionSegment())
        # Connect signal to segment object
        self.scan_list[-1].is_changed.connect(lambda: self.scan_plot.updatePlot(self.scan_list))
        # Update plot
        self.scan_plot.updatePlot(self.scan_list)
        self.scan_plot.show()

    def removeSegment(self):
        # Remove segment object from list
        self.scan_list.pop()
        # Update plot
        self.scan_plot.updatePlot(self.scan_list)

# class ScanFunctionHeader(QWidget):
#     def __init__(self):
#         super(ScanFunctionHeader, self).__init__()
#         # Create header for Scan Function object
#         self.header_layout = QVBoxLayout()
#         self.setLayout(self.header_layout)
#         self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
#         # Create labels
#         self.name_label = QLabel('Name')
#         self.header_layout.addWidget(self.name_label)
#         self.type_label = QLabel("Type")
#         self.header_layout.addWidget(self.type_label)
#         self.duration_label = QLabel("Duration")
#         self.header_layout.addWidget(self.duration_label)
#         self.startfreq_label = QLabel("Start Frequency")
#         self.header_layout.addWidget(self.startfreq_label)
#         self.endfreq_label = QLabel("End Frequency")
#         self.header_layout.addWidget(self.endfreq_label)
#         self.dutycycle_label = QLabel("Duty Cycle")
#         self.header_layout.addWidget(self.dutycycle_label)
#         self.stepres_label = QLabel("Step Resolution")
#         self.header_layout.addWidget(self.stepres_label)
#         # Set up table of analog output labels
#         self.analog_label = QTableWidget(ANALOG_ROWS, 1)
#         self.analog_label.horizontalHeader().hide()
#         self.analog_label.verticalHeader().hide()
#         self.analog_label.horizontalHeader().setDefaultSectionSize(WIDTH)
#         self.analog_label.verticalHeader().setDefaultSectionSize(HEIGHT)
#         self.analog_label.setFixedSize(WIDTH, HEIGHT*ANALOG_ROWS+2)
#         self.header_layout.addWidget(self.analog_label)
#         # Set up table of digital output labels
#         self.digital_label = QTableWidget(DIGITAL_ROWS, 1)
#         self.digital_label.horizontalHeader().hide()
#         self.digital_label.verticalHeader().hide()
#         self.digital_label.horizontalHeader().setDefaultSectionSize(WIDTH)
#         self.digital_label.verticalHeader().setDefaultSectionSize(HEIGHT)
#         self.digital_label.setFixedSize(WIDTH, HEIGHT*DIGITAL_ROWS+2)
#         self.header_layout.addWidget(self.digital_label)

class ScanFunctionSegment(QWidget):
    # Signal for updating plot
    is_changed = pyqtSignal()

    def __init__(self):
        super(ScanFunctionSegment, self).__init__()
        # Create layout for segment
        self.segment_layout = QVBoxLayout()
        self.setLayout(self.segment_layout)
        self.setFixedWidth(200)

        # Create label and box for name
        self.name_label = QLabel("Name")
        self.name_box = QLineEdit()
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_box)
        self.segment_layout.addLayout(self.name_layout)

        # Create table header to separate outputs
        self.output1_label = QLabel("Output 1")
        self.segment_layout.addWidget(self.output1_label)
        # Create table for parameters
        self.output1_table = OutputParameterTable()
        # Add table to layout
        self.segment_layout.addWidget(self.output1_table)
        # Signals for updating plot
        self.output1_table.type_box.activated[str].connect(self.isChanged)
        for row in range(1, PARAMETER_ROWS):
            self.output1_table.cellWidget(row, 1).textChanged.connect(self.isChanged)

        # Create table header to separate outputs
        self.output2_label = QLabel("Output 2")
        self.segment_layout.addWidget(self.output2_label)
        # Create table for parameters
        self.output2_table = OutputParameterTable()
        # Add table to layout
        self.segment_layout.addWidget(self.output2_table)
        # Signals for updating plot
        self.output2_table.type_box.activated[str].connect(self.isChanged)
        for row in range(1, PARAMETER_ROWS):
            self.output2_table.cellWidget(row, 1).textChanged.connect(self.isChanged)

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
        # Set up boxes
        for row in range(ANALOG_ROWS):
            self.analog_table.setCellWidget(row, 1, QLineEdit())

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
        # Set up boxes
        for row in range(DIGITAL_ROWS):
            self.digital_box = QComboBox()
            self.digital_box.addItem("False")
            self.digital_box.addItem("True")
            self.digital_table.setCellWidget(row, 1, self.digital_box)

    def isChanged(self):
        self.is_changed.emit()

class OutputParameterTable(QTableWidget):
    def __init__(self):
        super(OutputParameterTable, self).__init__()

        # Set up sizes and hide default headers
        self.setRowCount(PARAMETER_ROWS)
        self.setColumnCount(2)
        self.horizontalHeader().hide()
        self.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.setFixedHeight(HEIGHT*PARAMETER_ROWS+2)
        # Set up labels
        self.setItem(0, 0, QTableWidgetItem("Type"))
        self.setItem(1, 0, QTableWidgetItem("Duration"))
        self.setItem(2, 0, QTableWidgetItem("Start Freq"))
        self.setItem(3, 0, QTableWidgetItem("End Freq"))
        self.setItem(4, 0, QTableWidgetItem("Duty Cycle"))
        self.setItem(5, 0, QTableWidgetItem("Step Res"))
        # Make labels uneditable
        for row in range(0, PARAMETER_ROWS):
            self.item(row, 0).setFlags(Qt.ItemIsEnabled)

        # Set up type option box
        self.type_box = QComboBox()
        self.type_box.addItem("Fixed")
        self.type_box.addItem("Ramp")
        self.type_box.addItem("Mass Analysis")
        self.type_box.addItem("Dump")
        self.type_box.addItem("Custom")
        self.setCellWidget(0, 1, self.type_box)

        # Set up other boxes
        for row in range(0, PARAMETER_ROWS):
            if row is not 0:
                self.setCellWidget(row, 1, QLineEdit())

        # Signal character for Arduino - default is 'f' for Fixed
        self.type = 'f'
        self.updateType("Fixed")

        # Trigger update segment type
        self.type_box.activated[str].connect(self.updateType)

    def updateType(self, type):
        # Ensure start and end frequencies aren't mirroring each other from previously being a fixed segment
        try:
            self.cellWidget(2, 1).textChanged.disconnect()
        except:
            pass

        if type == "Fixed":
            self.type = 'f'
            self.cellWidget(3, 1).setEnabled(False)
            self.cellWidget(5, 1).setEnabled(False)
            self.cellWidget(1, 1).setText("10")
            self.cellWidget(2, 1).setText("100000")
            self.cellWidget(3, 1).setText("100000")
            # Connect start and end frequencies in fixed segment
            self.cellWidget(2, 1).textChanged.connect(self.cellWidget(3, 1).setText)
            self.cellWidget(4, 1).setText("50")
        elif type == "Ramp":
            self.type = 'r'
            self.cellWidget(3, 1).setEnabled(True)
            self.cellWidget(5, 1).setEnabled(False)
            self.cellWidget(1, 1).setText("10")
            self.cellWidget(2, 1).setText("100000")
            self.cellWidget(3, 1).setText("200000")
            self.cellWidget(4, 1).setText("50")
        elif type == "Mass Analysis":
            self.type = 'm'
            self.cellWidget(3, 1).setEnabled(True)
            self.cellWidget(5, 1).setEnabled(True)
            self.cellWidget(1, 1).setText("10")
            self.cellWidget(2, 1).setText("400000")
            self.cellWidget(3, 1).setText("100000")
            self.cellWidget(4, 1).setText("50")
            self.cellWidget(5, 1).setText("5")
        elif type == "Dump":
            self.type = 'd'
            self.cellWidget(3, 1).setEnabled(True)
            self.cellWidget(5, 1).setEnabled(True)
        elif type == "Custom":
            self.type = 'c'
            self.cellWidget(3, 1).setEnabled(True)
            self.cellWidget(5, 1).setEnabled(True)

class ScanFunctionPlot(pg.PlotWidget):
    def __init__(self):
        super(ScanFunctionPlot, self).__init__()

    def generatePlotData(self, scan_function):
        self.output1_x_values = []
        self.output1_y_values = []
        self.output2_x_values = []
        self.output2_y_values = []
        for segment in scan_function:
            # Segment start time and frequency
            try:
                self.output1_x_values.append(self.output1_x_values[-1])
                self.output2_x_values.append(self.output2_x_values[-1])
            except:
                self.output1_x_values.append(0)
                self.output2_x_values.append(0)
            try:
                self.output1_y_values.append(float(segment.output1_table.cellWidget(2, 1).text()))
                self.output2_y_values.append(float(segment.output2_table.cellWidget(2, 1).text()))
            except:
                self.output1_y_values.append(0)
                self.output2_y_values.append(0)
            # Segment end time and frequency
            try:
                self.output1_x_values.append(float(segment.output1_table.cellWidget(1, 1).text()) + float(self.output1_x_values[-1]))
                self.output2_x_values.append(float(segment.output2_table.cellWidget(1, 1).text()) + float(self.output2_x_values[-1]))
            except:
                self.output1_x_values.append(0)
                self.output2_x_values.append(0)
            try:
                self.output1_y_values.append(float(segment.output1_table.cellWidget(3, 1).text()))
                self.output2_y_values.append(float(segment.output2_table.cellWidget(3, 1).text()))
            except:
                self.output1_y_values.append(0)
                self.output2_y_values.append(0)

    def updatePlot(self, scan_function):
        self.generatePlotData(scan_function)
        self.plotItem.clear()
        self.plotItem.plot(self.output1_x_values, self.output1_y_values, pen='r')
        self.plotItem.plot(self.output2_x_values, self.output2_y_values, pen='b')
