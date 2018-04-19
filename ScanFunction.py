from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import OrderedDict
from math import *
import pyqtgraph as pg
import json
import pdb

WIDTH = 95
HEIGHT = 24
ANALOG_ROWS = 8
DIGITAL_ROWS = 12
# PARAMETERS = 8

# def convertFreqToMass(constant, frequency):
#     try:
#         # Convert frequencies
#         mass = str(round(float(constant)/pow(float(frequency), 2), 5))
#     except:
#         mass = frequency
#
#     return mass

# def convertMassToFreq(constant, mass):
#     try:
#         # Convert m/z values
#         frequency = str(round(sqrt(float(constant)/float(mass)), 5))
#     except:
#         frequency = mass
#
#     return frequency

class ScanFunction(object):
    def __init__(self, main_window):
        # Create list for holding segment objects
        self.scan_list = []
        # Create header for scan function object
        # self.header = ScanFunctionHeader()
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

    # def convertToMass(self, drive_constant, tickle_constant):
    #     for segment in self.scan_list:
    #         for output in segment.output_list:
    #             for name, [label, parameter] in output.parameter_dict.items():
    #                 if name in ['Start', 'End']:
    #                     label.setText(name + " (m/z)")
    #                     parameter.setText(convertFreqToMass(drive_constant, parameter.text()))
    #             try:
    #                 for name, [label, parameter] in output.tickle_layout.tickle_dict.items():
    #                     if name in ['Start', 'End']:
    #                         label.setText(name + " (m/z)")
    #                         parameter.setText(convertFreqToMass(tickle_constant, parameter.text()))
    #             except:
    #                 pass

    # def convertToFrequency(self, drive_constant, tickle_constant):
    #     for segment in self.scan_list:
    #         for output in segment.output_list:
    #             for name, [label, parameter] in output.parameter_dict.items():
    #                 if name in ['Start', 'End']:
    #                     label.setText(name + " (Hz)")
    #                     parameter.setText(convertMassToFreq(drive_constant, parameter.text()))
    #             try:
    #                 for name, [label, parameter] in output.tickle_layout.tickle_dict.items():
    #                     if name in ['Start', 'End']:
    #                         label.setText(name + " (Hz)")
    #                         parameter.setText(convertMassToFreq(tickle_constant, parameter.text()))
    #             except:
    #                 pass

    def addSegment(self, position):
        if position <= len(self.main_window.scan_function.scan_list) and position > -1:
            # Add new segment object to list
            self.new_segment = ScanFunctionSegment(self.analog_labels, self.digital_labels)
            self.scan_list.insert(position, self.new_segment)
            # Connect signal to segment object
            self.new_segment.is_changed.connect(lambda: self.scan_plot.updatePlot(self.scan_list))
            # Update plot
            self.scan_plot.updatePlot(self.scan_list)
            self.scan_plot.show()
            # Function to copy parameters from previous segment
            if position > 0:
                self.new_segment.convertFromDictionary(self.scan_list[position-1].convertToDictionary())
            # Create new widget in main window, recreate any following widgets so order is correct
            for segment in range(position, len(self.main_window.scan_function.scan_list)):
                self.main_window.scan_area.widget().layout().addWidget(self.scan_list[segment])
                self.scan_list[segment].updatePosition(segment+1)
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
            self.scan_plot.updatePlot(self.scan_list)
            # Fix segment numbering
            for segment in range(position, len(self.main_window.scan_function.scan_list)):
                self.scan_list[segment].updatePosition(segment+1)
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

        # Make dictionary for scan fucntion
    # Function for converting scan function to dictionary
    def convertToDictionary(self):
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

        # Show position number
        self.position_label = QLabel()
        self.position_label.setAlignment(Qt.AlignCenter)
        self.segment_layout.addWidget(self.position_label)

        # Create label and box for name
        self.name_label = QLabel("Name")
        self.name_box = QLineEdit()
        self.name_label.setFixedWidth(WIDTH)
        self.name_box.setFixedWidth(WIDTH)
        self.name_layout = QHBoxLayout()
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_box)
        self.segment_layout.addLayout(self.name_layout)

        # Create label and box for duration
        self.duration_label = QLabel("Duration (ms)")
        self.duration_box = QLineEdit("0")
        self.duration_label.setFixedWidth(WIDTH)
        self.duration_box.setFixedWidth(WIDTH)
        self.duration_box.textChanged.connect(self.isChanged)
        self.duration_layout = QHBoxLayout()
        self.duration_layout.addWidget(self.duration_label)
        self.duration_layout.addWidget(self.duration_box)
        self.segment_layout.addLayout(self.duration_layout)

        # Create label and box for choosing to record data
        self.data_record_label = QLabel("Record data")
        self.data_record_box = QComboBox()
        self.data_record_box.addItem("False")
        self.data_record_box.addItem("True")
        self.data_record_box.currentTextChanged.connect(self.colorDataRecordBox)
        self.data_record_label.setFixedWidth(WIDTH)
        self.data_record_box.setFixedWidth(WIDTH)
        self.data_record_layout = QHBoxLayout()
        self.data_record_layout.addWidget(self.data_record_label)
        self.data_record_layout.addWidget(self.data_record_box)
        self.segment_layout.addLayout(self.data_record_layout)

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
            self.analog_table.setItem(row, 0, QTableWidgetItem(analog_labels[row]))
            self.analog_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        # Set up boxes
        for row in range(ANALOG_ROWS):
            self.analog_table.setCellWidget(row, 1, QLineEdit("0"))

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
        for row in range(DIGITAL_ROWS):
            self.digital_table.setItem(row, 0, QTableWidgetItem(digital_labels[row]))
            self.digital_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        # Set up boxes
        for row in range(DIGITAL_ROWS):
            self.digital_box = QComboBox()
            self.digital_box.addItem("False")
            self.digital_box.addItem("True")
            self.digital_table.setCellWidget(row, 1, self.digital_box)
            self.digital_table.cellWidget(row, 1).currentTextChanged.connect(self.colorDigitalBox)

    def updatePosition(self, position):
        self.position_label.setText(str(position))

    def colorDataRecordBox(self):
        if self.data_record_box.currentText() == 'True':
            self.data_record_box.setStyleSheet("QComboBox {background-color: green}")
        else:
            self.data_record_box.setStyleSheet("QComboBox {background-color: white}")

    def colorDigitalBox(self):
        for row in range(DIGITAL_ROWS):
            if self.digital_table.cellWidget(row, 1).currentText() == 'True':
                self.digital_table.item(row, 0).setBackground(QBrush(QColor(0, 255, 0)))
            else:
                self.digital_table.item(row, 0).setBackground(QBrush(QColor(255, 255, 255)))

    def convertToDictionary(self):
        # Dictionary to hold segment parameters
        self.segment_data = {}
        # Write name to dictionary
        self.segment_data['Name'] = self.name_box.text()
        # Write duration to dictionary
        try:
            self.segment_data['Duration'] = float(self.duration_box.text())
        except:
            self.segment_data['Duration'] = 0
        # Write data record condition to dictionary
        self.segment_data['Record'] = self.data_record_box.currentText()

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
                self.segment_data['Analog'].append(0)

        # Read digital values from table
        self.segment_data['Digital'] = []
        for row in range(self.digital_table.rowCount()):
            self.segment_data['Digital'].append(self.digital_table.cellWidget(row, 1).currentText())

        # Return segment dictionary
        return self.segment_data

    def convertFromDictionary(self, segment_data):
        # Update name
        self.name_box.setText(segment_data['Name'])
        # Update duration
        self.duration_box.setText(str(segment_data['Duration']))
        # Update data record condition
        self.data_record_box.setCurrentText(segment_data['Record'])
        # Update outputs
        for output_data_index in range(len(segment_data['Outputs'])):
            self.output_list[output_data_index].convertFromDictionary(segment_data['Outputs'][output_data_index])
        # Update analog values
        for row in range(self.analog_table.rowCount()):
            self.analog_table.cellWidget(row, 1).setText(str(segment_data['Analog'][row]))
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
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.addWidget(self.line, 0, 0, 1, 2)
        self.header = QLabel("Output " + str(number+1))
        if number == 0:
            self.header.setStyleSheet("QLabel {color : red}")
        elif number == 1:
            self.header.setStyleSheet("QLabel {color : orange}")
        elif number == 2:
            self.header.setStyleSheet("QLabel {color : green}")
        self.addWidget(self.header, 1, 0, 1, 2)

        # Create parameters
        self.parameter_dict = OrderedDict()
        # self.parameter_dict['Type'] = [QLabel(), QComboBox()]
        self.parameter_dict['Start'] = [QLabel('  Start (Hz)'), QLineEdit("0")]
        self.parameter_dict['End'] = [QLabel('  End (Hz)'), QLineEdit("0")]
        self.parameter_dict['Duty Cycle'] = [QLabel('  Duty Cycle (%)'), QLineEdit("0")]
        self.parameter_dict['Tickle'] = [QLabel('Excitation ' + str(number+1)), QComboBox()]
        self.parameter_dict['Amplitude'] = [QLabel('  Amplitude (V)'), QLineEdit("0")]
        self.parameter_dict['Phase'] = [QLabel('  Phase (deg)'), QComboBox()]

        # Place widgets in layout
        self.layout_position = 2
        for name, [label, parameter] in self.parameter_dict.items():
            # if name in ['Start', 'End']:
            #     label.setText(name + " (Hz)")
            # else:
            #     label.setText(name)
            label.setFixedWidth(WIDTH)
            parameter.setFixedWidth(WIDTH)
            self.addWidget(label, self.layout_position, 0)
            self.addWidget(parameter, self.layout_position, 1)
            self.layout_position += 1

            size_policy = QSizePolicy()
            size_policy.setRetainSizeWhenHidden(True)
            label.setSizePolicy(size_policy)
            parameter.setSizePolicy(size_policy)

        # Create supplementary tickle layout
        # if number is not 2:
        #     self.tickle_layout = SupplementaryTickleLayout()
        #     self.addWidget(self.tickle_layout, 10, 0, 1, 2)

        # Set up type options
        # self.parameter_dict['Type'][1].addItem("None")
        # self.parameter_dict['Type'][1].addItem("Fixed")
        # self.parameter_dict['Type'][1].addItem("Ramp")
        # self.parameter_dict['Type'][1].addItem("Mass Analysis")
        # self.parameter_dict['Type'][1].addItem("Dump")
        # self.parameter_dict['Type'][1].addItem("Custom")

        # Output 3 special options
        # if number is not 2:
        #     self.parameter_dict['Type'][1].addItem("CID")
        #     self.parameter_dict['Type'][1].addItem("Isolation")

        # Set up phase options
        self.parameter_dict['Phase'][1].addItem("0")
        self.parameter_dict['Phase'][1].addItem("180")

        # Set up tickle division options
        self.parameter_dict['Tickle'][1].addItem("Drive / 2")
        self.parameter_dict['Tickle'][1].addItem("Drive / 4")
        self.parameter_dict['Tickle'][1].addItem("Drive / 8")
        self.parameter_dict['Tickle'][1].addItem("Drive / 16")
        if number is not 2:
            self.parameter_dict['Tickle'][1].addItem("Output 3")

        # Connect trigger for updating tickle options
        self.parameter_dict['Tickle'][1].currentTextChanged.connect(self.updateTickleOptions)

        # Default type for output
        # self.updateType("None")

        # Trigger update segment type
        # self.parameter_dict['Type'][1].activated[str].connect(self.updateType)

    def updateTickleOptions(self, tickle_choice):
        # Change available options if using drive divided tickle or output 3 as tickle
        if tickle_choice == "Output 3":
            self.parameter_dict['Amplitude'][1].hide()
            self.parameter_dict['Phase'][1].hide()
        else:
            self.parameter_dict['Amplitude'][1].show()
            self.parameter_dict['Phase'][1].show()

    # def updateType(self, type):
    #     if type == "None":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name is not 'Type':
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "Fixed":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type', 'Start', 'Duty Cycle']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "Ramp":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type', 'Start', 'End', 'Duty Cycle']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "Mass Analysis":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type', 'Start', 'End', 'Duty Cycle', 'Tickle Phase', 'Tickle Voltage', 'Eject at beta']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "Dump":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "Custom":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.hide()
    #         except:
    #             pass
    #
    #     elif type == "CID":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type', 'Start', 'Duty Cycle']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.show()
    #             self.tickle_layout.tickle_dict['End'][0].hide()
    #             self.tickle_layout.tickle_dict['End'][1].hide()
    #         except:
    #             pass
    #
    #
    #     elif type == "Isolation":
    #         for name, [label, parameter] in self.parameter_dict.items():
    #             if name in ['Type', 'Start', 'Duty Cycle']:
    #                 label.show()
    #                 parameter.show()
    #             else:
    #                 label.hide()
    #                 parameter.hide()
    #         try:
    #             self.tickle_layout.show()
    #             self.tickle_layout.tickle_dict['End'][0].show()
    #             self.tickle_layout.tickle_dict['End'][1].show()
    #         except:
    #             pass
    #
    #     else:
    #         pass
    #
    #     # Reset values and boxes for hidden parameters
    #     for name, [label, parameter] in self.parameter_dict.items():
    #         if parameter.isHidden():
    #             try:
    #                 parameter.setText("")
    #             except:
    #                 parameter.setCurrentIndex(0)
    #     try:
    #         if self.tickle_layout.isHidden():
    #             for name, [label, parameter] in self.tickle_layout.tickle_dict.items():
    #                 try:
    #                     parameter.setText("")
    #                 except:
    #                     parameter.setCurrentIndex(0)
    #     except:
    #         pass

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
                        # Tickle phase is integer
                        self.output_data[name] = int(parameter.currentText())
                    except:
                        try:
                            # Type parameter has current text
                            self.output_data[name] = parameter.currentText()
                        except:
                            self.output_data[name] = 0
        # Write supplementary tickle parameters to dictionary
        # try:
        #     if self.tickle_layout.isHidden() == False:
        #         self.output_data["Supplementary Tickle"] = self.tickle_layout.convertToDictionary()
        # except:
        #     pass
        # Return output dictionary
        return self.output_data

    def convertFromDictionary(self, output_data):
        # Update parameters
        # self.updateType(str(output_data["Type"]))
        for label, parameter_data in output_data.items():
            try:
                self.parameter_dict[label][1].setText(str(parameter_data))
            except:
                pass
            try:
                self.parameter_dict[label][1].setCurrentText(str(parameter_data))
            except:
                pass
        # Update supplementary tickle parameters
        # try:
        #     self.tickle_layout.convertFromDictionary(output_data["Supplementary Tickle"])
        # except:
        #     pass

# class SupplementaryTickleLayout(QFrame):
#     def __init__(self):
#         super(SupplementaryTickleLayout, self).__init__()
#         # Set layout
#         self.setLayout(QGridLayout())
#         self.setFixedWidth(WIDTH*2)
#         self.layout().setContentsMargins(0, 0, 0, 0)
#         self.layout().setAlignment(Qt.AlignLeft)
#         self.size_policy = QSizePolicy()
#         self.size_policy.setRetainSizeWhenHidden(True)
#         self.setSizePolicy(self.size_policy)
#         # Create header
#         self.layout().addWidget(QLabel("Supplementary Tickle"), 0, 0, 1, 2)
#         # Create labels and boxes
#         self.tickle_dict = OrderedDict()
#         self.tickle_dict['Start'] = [QLabel(), QLineEdit()]
#         self.tickle_dict['End'] = [QLabel(), QLineEdit()]
#         self.tickle_dict['Duty Cycle'] = [QLabel(), QLineEdit()]
#         self.tickle_dict['Tickle Voltage'] = [QLabel(), QLineEdit()]
#         self.tickle_dict['Tickle Phase'] = [QLabel(), QComboBox()]
#         # Place labels and boxes in layout
#         self.layout_position = 1
#         for name, [label, parameter] in self.tickle_dict.items():
#             if name in ['Start', 'End']:
#                 label.setText(name + " (Hz)")
#             else:
#                 label.setText(name)
#             label.setFixedWidth(WIDTH-6)
#             parameter.setFixedWidth(WIDTH)
#             parameter.setSizePolicy(self.size_policy)
#             self.layout().addWidget(label, self.layout_position, 0)
#             self.layout().addWidget(parameter, self.layout_position, 1)
#             self.layout_position += 1
#         # Set up phase options
#         self.tickle_dict['Tickle Phase'][1].addItem("0")
#         self.tickle_dict['Tickle Phase'][1].addItem("180")
#
#     def convertToDictionary(self):
#         # Write tickle parameters to dictionary
#         self.tickle_data = {}
#         for name, [label, parameter] in self.tickle_dict.items():
#             if parameter.isHidden() == False:
#                 try:
#                     # Most parameters have text - convert to number
#                     self.tickle_data[name] = float(parameter.text())
#                 except:
#                     try:
#                         # Tickle division is integer
#                         self.tickle_data[name] = int(parameter.currentText())
#                     except:
#                         try:
#                             # Type parameter has current text
#                             self.tickle_data[name] = parameter.currentText()
#                         except:
#                             self.tickle_data[name] = None
#         # Return output dictionary
#         return self.tickle_data
#
#     def convertFromDictionary(self, tickle_data):
#         # Update parameters
#         for label, parameter_data in tickle_data.items():
#             try:
#                 self.tickle_dict[label][1].setText(str(parameter_data))
#             except:
#                 pass
#             try:
#                 self.tickle_dict[label][1].setCurrentText(str(parameter_data))
#             except:
#                 pass

class ScanFunctionPlot(pg.PlotWidget):
    def __init__(self):
        super(ScanFunctionPlot, self).__init__()
        # Create time axis label
        self.setLabel('bottom', text='Time', units='s')
        self.setLabel('left', text='Frequency', units='Hz')

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
                # if segment.output_list[output].parameter_dict['Type'][1].currentText() in ["Fixed", "CID"]:
                #     self.y_values[output].append(self.y_values[output][-1])
                # else:
                    try:
                        self.y_values[output].append(float(segment.output_list[output].parameter_dict['End'][1].text()))
                    except:
                        self.y_values[output].append(0)

    def updatePlot(self, scan_function):
        # if frequency_mode == True:
        #     self.setLabel('left', text='Frequency', units='Hz')
        # else:
        #     self.setLabel('left', text='m/z', units='Th')

        self.generatePlotData(scan_function)
        self.plotItem.clear()
        for output in range(3):
            self.plotItem.plot(self.x_values, self.y_values[output], pen=output)
