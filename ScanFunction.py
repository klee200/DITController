from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import OrderedDict
from math import *
import pyqtgraph as pg
import json
import pdb

WIDTH = 80
HEIGHT = 24
ANALOG_ROWS = 16
DIGITAL_ROWS = 21
PARAMETERS = 6

def convertFreqToMass(constant, frequency):
    try:
        # Convert start frequencies
        mass = str(round(float(constant)/pow(float(frequency), 2), 5))
    except:
        mass = frequency

    return mass

def convertMassToFreq(constant, mass):
    try:
        # Convert start m/z values
        frequency = str(round(sqrt(float(constant)/float(mass)), 5))
    except:
        frequency = mass

    return frequency

class ScanFunction(object):
    def __init__(self, main_window):
        # Create header for scan function object
        # self.header = ScanFunctionHeader()
        # Create list for holding segment objects
        self.scan_list = []
        # Create digital labels used to save digital output names
        self.analog_labels = []
        for row in range(ANALOG_ROWS):
            self.analog_labels.append("A" + str(row+1))
        self.digital_labels = []
        for row in range(DIGITAL_ROWS):
            self.digital_labels.append("D" + str(row+1))
        # Create updating plot object
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        self.scan_plot = ScanFunctionPlot()
        self.main_window = main_window

    def convertToMass(self, conversion_constant):
        for segment in self.scan_list:
            for output in segment.output_list:
                for name, [label, parameter] in output.parameter_dict.items():
                    if name == 'Start':
                        output.parameter_dict['Start'][1].setText(convertFreqToMass(conversion_constant, parameter.text()))
                        # if parameter.isHidden() == False:
                        #     output.parameter_dict['Start m/z'][1].show()
                        # parameter.hide()
                    elif name == 'End':
                        output.parameter_dict['End'][1].setText(convertFreqToMass(conversion_constant, parameter.text()))
                        # if parameter.isHidden() == False:
                        #     output.parameter_dict['End m/z'][1].show()
                        # parameter.hide()

    def convertToFrequency(self, conversion_constant):
        for segment in self.scan_list:
            for output in segment.output_list:
                for name, [label, parameter] in output.parameter_dict.items():
                    if name == 'Start':
                        output.parameter_dict['Start'][1].setText(convertMassToFreq(conversion_constant, parameter.text()))
                        # if parameter.isHidden() == False:
                        #     output.parameter_dict['Start'][1].show()
                        # parameter.hide()
                    elif name == 'End':
                        output.parameter_dict['End'][1].setText(convertMassToFreq(conversion_constant, parameter.text()))
                        # if parameter.isHidden() == False:
                        #     output.parameter_dict['End'][1].show()
                        # parameter.hide()

    def addSegment(self, position):
        if position <= len(self.main_window.scan_function.scan_list) and position > -1:
            # Add new segment object to list
            self.new_segment = ScanFunctionSegment(self.analog_labels, self.digital_labels)
            self.scan_list.insert(position, self.new_segment)
            # Connect signal to segment object
            self.new_segment.is_changed.connect(lambda: self.scan_plot.updatePlot(self.scan_list, self.main_window.frequency_button.isChecked()))
            # Update plot
            self.scan_plot.updatePlot(self.scan_list, self.main_window.frequency_button.isChecked())
            self.scan_plot.show()
            # Function to copy parameters from previous segment
            if position > 0:
                self.new_segment.convertFromDictionary(self.scan_list[position-1].convertToDictionary())
            # Create new widget in main window, recreate any following widgets so order is correct
            for segment in range(position, len(self.main_window.scan_function.scan_list)):
                self.main_window.scan_area.widget().layout().addWidget(self.main_window.scan_function.scan_list[segment])
            # Announce creation of new segment
            self.main_window.announcer.appendPlainText("New Segment added at position " + str(position+1))
        else:
            # Announce failure to make segment
            self.main_window.announcer.appendPlainText("Invalid position")

        return self.new_segment

    def removeSegment(self, position):
        try:
            # Remove segment widget from layout
            self.main_window.scan_function.scan_list[position].hide()
            self.main_window.scan_area.widget().layout().removeWidget(self.main_window.scan_function.scan_list[position])
            # Remove segment object from list
            self.scan_list.remove(self.scan_list[position])
            # Update plot
            self.scan_plot.updatePlot(self.scan_list, self.main_window.frequency_button.isChecked())
            # Announce segment removal
            self.main_window.announcer.appendPlainText("Segment removed from position " + str(position+1))
        except:
            # If no segment, announce error
            self.main_window.announcer.appendPlainText("No segment to remove")

    def updateLabels(self, new_analog_labels, new_digital_labels):
        # Update list of labels
        self.analog_labels = new_analog_labels
        self.digital_labels = new_digital_labels
        # Change analog and digital labels
        for segment in self.scan_list:
            for row in range(ANALOG_ROWS):
                segment.analog_table.item(row, 0).setText(new_analog_labels[row])
            for row in range(DIGITAL_ROWS):
                segment.digital_table.item(row, 0).setText(new_digital_labels[row])

    # Function for converting scan function to dictionary
    def convertToDictionary(self):
        # Make dictionary for scan fucntion
        self.scan_function_dict = {}
        # Write labels to dictionary
        self.scan_function_dict['Analog Labels'] = self.analog_labels
        self.scan_function_dict['Digital Labels'] = self.digital_labels
        # List for segments in scan function
        self.scan_function_dict['Data'] = []
        # Create list of segment parameters with name labels
        for segment in self.scan_list:
            self.scan_function_dict['Data'].append(segment.convertToDictionary())

        # Dump json-like list into actual json object and return it
        return self.scan_function_dict

    def convertToJson(self):
        return json.dumps(self.convertToDictionary(), sort_keys=True, indent=4)

    def convertFromJson(self, scan_function_json):
        # Clear widgets from window
        for segment in self.scan_list:
            segment.hide()
            self.main_window.scan_area.widget().layout().removeWidget(segment)
        # Clear scan list
        self.scan_list.clear()
        # Create new segment object
        self.convertFromDictionary(json.loads(scan_function_json))

    def convertFromDictionary(self, scan_function_data):
        # Update labels
        self.updateLabels(scan_function_data['Analog Labels'], scan_function_data['Digital Labels'])
        # Make segments
        for segment_data in scan_function_data['Data']:
            self.addSegment(len(self.scan_list)).convertFromDictionary(segment_data)

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

    def __init__(self, analog_labels, digital_labels):
        super(ScanFunctionSegment, self).__init__()
        # Create layout for segment
        self.segment_layout = QVBoxLayout()
        self.setLayout(self.segment_layout)
        self.setFixedWidth(WIDTH*2+10)

        # Create label and box for name
        self.name_label = QLabel("Name")
        self.name_box = QLineEdit()
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_box)
        self.segment_layout.addLayout(self.name_layout)

        # Create label and box for duration
        self.duration_label = QLabel("Duration")
        self.duration_box = QLineEdit("10")
        self.duration_box.setFixedWidth(WIDTH)
        self.duration_box.textChanged.connect(self.isChanged)
        self.duration_layout = QHBoxLayout()
        self.duration_layout.addWidget(self.duration_label)
        self.duration_layout.addWidget(self.duration_box)
        self.segment_layout.addLayout(self.duration_layout)

        # Create Output sections
        self.output_list = []
        for output in range(3):
            self.output_list.append(OutputParameterLayout(output))
            self.segment_layout.addLayout(self.output_list[output])
            for name, [label, parameter] in self.output_list[output].parameter_dict.items():
                try:
                    parameter.textChanged.connect(self.isChanged)
                except:
                    parameter.currentTextChanged.connect(self.isChanged)

        # Create table for analog outputs
        self.analog_table = QTableWidget(ANALOG_ROWS, 2)
        # Add table to layout
        self.segment_layout.addWidget(self.analog_table)
        # Set up sizes and hide default headers
        self.analog_table.horizontalHeader().hide()
        self.analog_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.analog_table.setFixedWidth(WIDTH*2+2)
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
        self.digital_table.setFixedWidth(WIDTH*2+2)
        self.digital_table.verticalHeader().hide()
        self.digital_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.digital_table.setFixedHeight(HEIGHT*DIGITAL_ROWS+2)
        # Set up labels
        for row in range(ANALOG_ROWS):
            self.analog_table.setItem(row, 0, QTableWidgetItem(analog_labels[row]))
            self.analog_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        for row in range(DIGITAL_ROWS):
            self.digital_table.setItem(row, 0, QTableWidgetItem(digital_labels[row]))
            self.digital_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        # Set up boxes
        for row in range(DIGITAL_ROWS):
            self.digital_box = QComboBox()
            self.digital_box.addItem("False")
            self.digital_box.addItem("True")
            self.digital_table.setCellWidget(row, 1, self.digital_box)

    def convertToDictionary(self):
        # Dictionary to hold segment parameters
        self.segment_data = {}
        # Write name to dictionary
        self.segment_data['Name'] = self.name_box.text()
        # Write duration to dictionary
        self.segment_data['Duration'] = float(self.duration_box.text())

        # Write output parameters to dictionary
        self.segment_data['Outputs'] = []
        for output in self.output_list:
            self.segment_data['Outputs'].append(output.convertToDictionary())

        # Read analog values from table
        self.segment_data['Analog'] = []
        for row in range(self.analog_table.rowCount()):
            try:
                self.segment_data['Analog'].append(float(self.analog_table.cellWidget(row, 1).text()))
            except:
                self.segment_data['Analog'].append(None)

        # Read digital values from table
        self.segment_data['Digital'] = []
        for row in range(self.digital_table.rowCount()):
            try:
                self.segment_data['Digital'].append(self.digital_table.cellWidget(row, 1).currentText())
            except:
                self.segment_data['Digital'].append(None)

        # Return segment dictionary
        return self.segment_data

    def convertFromDictionary(self, segment_data):
        # Update name
        self.name_box.setText(segment_data['Name'])
        # Update duration
        self.duration_box.setText(str(segment_data['Duration']))
        # Update outputs
        for output_data in segment_data['Outputs']:
            self.output_list[segment_data['Outputs'].index(output_data)].convertFromDictionary(output_data)
        # Update analog values
        for row in range(self.analog_table.rowCount()):
            self.analog_table.cellWidget(row, 1).setText(segment_data['Analog'][row])
        # Update digital values
        for row in range(self.digital_table.rowCount()):
            if segment_data['Digital'][row] == 'False':
                self.digital_table.cellWidget(row, 1).setCurrentIndex(0)
            elif segment_data['Digital'][row] == 'True':
                self.digital_table.cellWidget(row, 1).setCurrentIndex(1)

    def isChanged(self):
        self.is_changed.emit()

class OutputParameterLayout(QGridLayout):
    def __init__(self, number):
        super(OutputParameterLayout, self).__init__()

        # Create header
        self.header = QLabel("Output " + str(number+1))
        self.addWidget(self.header)

        # Create parameters
        self.parameter_dict = OrderedDict()
        self.parameter_dict['Type'] = [QLabel(), QComboBox()]
        self.parameter_dict['Start'] = [QLabel(), QLineEdit()]
        # self.parameter_dict['Start m/z'] = [QLabel(), QLineEdit()]
        self.parameter_dict['End'] = [QLabel(), QLineEdit()]
        # self.parameter_dict['End m/z'] = [QLabel(), QLineEdit()]
        self.parameter_dict['Duty Cycle'] = [QLabel(), QLineEdit()]
        self.parameter_dict['Step'] = [QLabel(), QLineEdit()]
        self.parameter_dict['Tickle'] = [QLabel(), QComboBox()]

        # Place widgets in layout
        self.layout_position = 1
        for name, [label, parameter] in self.parameter_dict.items():
            label.setText(name)
            self.addWidget(label, self.layout_position, 0)
            self.addWidget(parameter, self.layout_position, 1)
            self.layout_position += 1

            # if name not in ['Start m/z', 'End m/z']:
            size_policy = QSizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            label.setSizePolicy(size_policy)
            parameter.setSizePolicy(size_policy)

        # Set up type options
        self.parameter_dict['Type'][1].addItem("None")
        self.parameter_dict['Type'][1].addItem("Fixed")
        self.parameter_dict['Type'][1].addItem("Ramp")
        self.parameter_dict['Type'][1].addItem("Mass Analysis")
        self.parameter_dict['Type'][1].addItem("Dump")
        self.parameter_dict['Type'][1].addItem("Custom")

        # Set up tickle division options
        self.parameter_dict['Tickle'][1].addItem("2")
        self.parameter_dict['Tickle'][1].addItem("4")
        self.parameter_dict['Tickle'][1].addItem("8")
        self.parameter_dict['Tickle'][1].addItem("16")

        # Default type for output
        self.updateType("None")

        # Trigger update segment type
        self.parameter_dict['Type'][1].activated[str].connect(self.updateType)

    def updateType(self, type):
        if type == "None":
            for name, [label, parameter] in self.parameter_dict.items():
                if name is not 'Type':
                    label.hide()
                    parameter.hide()

        elif type == "Fixed":
            for name, [label, parameter] in self.parameter_dict.items():
                if name in ['Type', 'Start', 'Duty Cycle']:
                    label.show()
                    parameter.show()
                else:
                    label.hide()
                    parameter.hide()

        elif type == "Ramp":
            for name, [label, parameter] in self.parameter_dict.items():
                if name in ['Type', 'Start', 'End', 'Duty Cycle']:
                    label.show()
                    parameter.show()
                else:
                    label.hide()
                    parameter.hide()

        elif type == "Mass Analysis":
            for name, [label, parameter] in self.parameter_dict.items():
                if name in ['Type', 'Start', 'End', 'Duty Cycle', 'Step', 'Tickle']:
                    label.show()
                    parameter.show()
                else:
                    label.hide()
                    parameter.hide()

        elif type == "Dump":
            for name, [label, parameter] in self.parameter_dict.items():
                if name in ['Type']:
                    label.show()
                    parameter.show()
                else:
                    label.hide()
                    parameter.hide()

        elif type == "Custom":
            for name, [label, parameter] in self.parameter_dict.items():
                if name in ['Type']:
                    label.show()
                    parameter.show()
                else:
                    label.hide()
                    parameter.hide()

        else:
            pass

        for name, [label, parameter] in self.parameter_dict.items():
            if parameter.isHidden():
                try:
                    parameter.setText("")
                except:
                    pass

    def convertToDictionary(self):
        # Write output parameters to dictionary
        self.output_data = {}
        for name, [label, parameter] in self.parameter_dict.items():
            if parameter.isHidden() == False:
                try:
                    # Most parameters have text - convert to number
                    self.output_data[name] = float(parameter.text())
                except:
                    try:
                        # Tickle division is integer
                        self.output_data[name] = int(parameter.currentText())
                    except:
                        try:
                            # Type parameter has current text
                            self.output_data[name] = parameter.currentText()
                        except:
                            self.output_data[name] = None
        # Return output dictionary
        return self.output_data

    def convertFromDictionary(self, output_data):
        # Update parameters
        for label, parameter_data in output_data.items():
            try:
                self.parameter_dict[label][1].setCurrentText(str(parameter_data))
                self.updateType(str(parameter_data))
            except:
                try:
                    self.parameter_dict[label][1].setText(str(parameter_data))
                except:
                    self.parameter_dict[label][1].setText(None)

class ScanFunctionPlot(pg.PlotWidget):
    def __init__(self):
        super(ScanFunctionPlot, self).__init__()
        # Create time axis label
        self.setLabel('bottom', text='Time', units='s')

    def generatePlotData(self, scan_function):
        self.x_values = []
        self.y_values = []
        for output in range(3):
            self.y_values.append([])
        self.digital_values = []
        for digital in range(21):
            self.digital_values.append([])

        for segment in scan_function:
            # Segment start time and frequency
            try:
                self.x_values.append(self.x_values[-1])
            except:
                self.x_values.append(0)

            for output in range(len(segment.output_list)):
                try:
                    self.y_values[output].append(float(segment.output_list[output].parameter_dict['Start'][1].text()))
                except:
                    self.y_values[output].append(0)

            # Segment end time and frequency
            try:
                self.x_values.append(float(segment.duration_box.text())/1000 + float(self.x_values[-1]))
            except:
                self.x_values.append(0)

            for output in range(len(segment.output_list)):
                if segment.output_list[output].parameter_dict['Type'][1].currentText() == "Fixed":
                    self.y_values[output].append(self.y_values[output][-1])
                else:
                    try:
                        self.y_values[output].append(float(segment.output_list[output].parameter_dict['End'][1].text()))
                    except:
                        self.y_values[output].append(0)

    def updatePlot(self, scan_function, frequency_mode):
        if frequency_mode == True:
            self.setLabel('left', text='Frequency', units='Hz')
        else:
            self.setLabel('left', text='m/z', units='Th')

        self.generatePlotData(scan_function)
        self.plotItem.clear()
        for output in range(3):
            self.plotItem.plot(self.x_values, self.y_values[output], pen=output)
