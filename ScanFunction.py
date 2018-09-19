from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from collections import OrderedDict
from math import *
import pyqtgraph as pg
import json
import pdb

NUM_OUTPUTS = 3
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

class ScanFunction(list):
    def __init__(self):
        super(ScanFunction, self).__init__()
        
    def reset(self, newScanFunction):
        while len(self) > 0:
            self.remove(self[0])
            print(len(self))
        for seg in newScanFunction:
            self.append(seg)
        print(len(self))
    
    
    
    
        # self.scanFunctionModel = ScanFunctionModel()
        # self.scanHeaderModel = ScanHeaderModel(self.scanFunctionModel)
        # self.mainWindow = mainWindow
        # Create header for scan function object
        # self.scanHeader = ScanHeader()
        # Create list for holding segment objects
        # self.scanList = []
        # Create digital labels used to save digital output names
        # self.analog_labels = []
        # for row in range(ANALOG_ROWS):
            # self.analog_labels.append("A" + str(row+1))
        # self.digital_labels = []
        # for row in range(DIGITAL_ROWS):
            # self.digital_labels.append("D" + str(row+1))
        # self.build_plot()
        
    # def build_plot(self):
        # Create updating plot object
        # pg.setConfigOption('background', 'w')
        # pg.setConfigOption('foreground', 'k')
        # self.scanPlot = ScanFunctionPlot()

    # def convertToMass(self, drive_constant, tickle_constant):
    #     for segment in self.scanList:
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
    #     for segment in self.scanList:
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

    def add_segment(self, position):
        if position <= len(self.scanList) and position > -1:
            # Add new segment object to list
            new_segment = ScanFunctionSegment(self.analog_labels, self.digital_labels)
            self.scanList.insert(position, new_segment)
            # Connect signal to segment object
            # self.new_segment.is_changed.connect(lambda: self.scanPlot.updatePlot(self.scanList))
            # Update plot
            # self.scanPlot.updatePlot(self.scanList)
            # Function to copy parameters from previous segment
            if position > 0:
                new_segment.convertFromDictionary(self.scanList[position-1].convertToDictionary())
        return self.scanList

    def remove_segment(self, position):
        try:
            # Remove segment widget from layout
            self.scanList[position].hide()
            self.mainWindow.scanArea.widget().layout().removeWidget(self.scanList[position])
            # Remove segment object from list
            self.scanList.remove(self.scanList[position])
            # Update plot
            self.scanPlot.updatePlot(self.scanList)
            # Fix segment numbering
            for segment in range(position, len(self.scanList)):
                self.scanList[segment].update_position(segment+1)
            # Announce segment removal
            self.mainWindow.announcer.appendPlainText("Segment removed from position " + str(position+1))
        except:
            # If no segment, announce error
            self.mainWindow.announcer.appendPlainText("No segment to remove")

    def updateLabels(self, new_analog_labels, new_digital_labels):
        # Update list of labels
        self.analog_labels = new_analog_labels
        self.digital_labels = new_digital_labels
        # Change analog and digital labels
        for segment in self.scanList:
            for row in range(ANALOG_ROWS):
                segment.analog_table.item(row, 0).setText(new_analog_labels[row])
            for row in range(DIGITAL_ROWS):
                segment.digital_table.item(row, 0).setText(new_digital_labels[row])

    def convertToDictionary(self):
        self.scan_function_dict = {}
        # Write labels to dictionary
        self.scan_function_dict['Analog Labels'] = self.analog_labels
        self.scan_function_dict['Digital Labels'] = self.digital_labels
        # List for segments in scan function
        self.scan_function_dict['Data'] = []
        # Create list of segment parameters with name labels
        for segment in self.scanList:
            self.scan_function_dict['Data'].append(segment.convertToDictionary())

        # Dump json-like list into actual json object and return it
        return self.scan_function_dict

    def convertToJson(self):
        return json.dumps(self.convertToDictionary(), sort_keys=True, indent=4)

    def convertFromJson(self, scan_function_json):
        # Create new segment object
        self.convertFromDictionary(json.loads(scan_function_json))

    def convertFromDictionary(self, scan_function_data):
        # Update labels
        self.updateLabels(scan_function_data['Analog Labels'], scan_function_data['Digital Labels'])
        # Make segments
        for segment_data in scan_function_data['Data']:
            self.add_segment(len(self.scanList)).convertFromDictionary(segment_data)

class ScanFunctionModel(QAbstractItemModel):
    def __init__(self):
        super(ScanFunctionModel, self).__init__()
        
        self.headerLabels = ["Name", "Duration (ms)", "Record Data"]
        for i in range(NUM_OUTPUTS):
            self.headerLabels.append("Output " + str(i + 1))
            self.headerLabels.append("Start (Hz)")
            self.headerLabels.append("End (Hz)")
            self.headerLabels.append("Duty Cycle (%)")
            self.headerLabels.append("Excitation " + str(i))
            self.headerLabels.append("Amplitude (V)")
            self.headerLabels.append("Phase (deg)")
        for i in range(ANALOG_ROWS):
            self.headerLabels.append("A" + str(i + 1))
        for i in range(DIGITAL_ROWS):
            self.headerLabels.append("D" + str(i + 1))
            
        self.build_scan_function()
                    
    def build_scan_function(self):
        self.scanFunction = ScanFunction()
        self.scanFunction.append(OrderedDict())
        for label in self.headerLabels:
            self.scanFunction[0][label] = 0
        
    def rowCount(self, parent):
        return len(self.headerLabels)
        
    def columnCount(self, parent):
        return len(self.scanFunction)
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self.headerLabels[section]
            else:
                return section + 1
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.scanFunction[index.column()][self.headerLabels[index.row()]]
        
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            self.scanFunction[index.column()][self.headerLabels[index.row()]] = value
        return True
        
    def flags(self, index):
        return Qt.ItemIsEditable | QAbstractItemModel.flags(self, index)
        
    def insertColumn(self, position, parent):
        if position <= len(self.scanFunction) and position >= 0:
            self.beginInsertColumns(parent, position, position)
            self.scanFunction.insert(position, OrderedDict())
            for label in self.headerLabels:
                self.scanFunction[position][label] = 0
            self.endInsertColumns()
            
            return True
        else:
            return False
            
    def removeColumn(self, position, parent):
        if position < len(self.scanFunction) and position >= 0:
            self.beginRemoveColumns(parent, position, position)
            self.scanFunction.remove(self.scanFunction[position])
            self.endRemoveColumns()
            
            return True
        else:
            return False
        


# class ScanHeaderModel(QAbstractItemModel):
    # def __init__(self, parent):
        # super(ScanHeaderModel, self).__init__()
        # self.setParent(parent)
    
    # def rowCount(self, parent):
        # return parent.rowCount()
            
# class ScanHeader(list):
    # def __init__(self):
        # super(ScanHeader, self).__init__()
        
        # self.append(QLabel())
        # self.append(QLabel("Name"))
        # self.append(QLabel("Duration (ms)"))
        # self.append(QLabel("Record data"))
        
        # for i in range(NUM_OUTPUTS):
            # line = QFrame()
            # line.setFrameShape(QFrame.HLine)
            # self.append(line)
            # self.append(QLabel("Output " + str(i + 1)))
            # self.append(QLabel("Start (Hz)"))
            # self.append(QLabel("End (Hz)"))
            # self.append(QLabel("Duty Cycle (%)"))
            # self.append(QLabel("Excitation " + str(i)))
            # self.append(QLabel("Amplitude (V)"))
            # self.append(QLabel("Phase (deg)"))
            
        # self.append(QTableWidget(ANALOG_ROWS, 1))
        # self.append(QTableWidget(DIGITAL_ROWS, 1))
        
        # Create layout for segment
        # self.setLayout(QVBoxLayout())
        # self.setFixedWidth(WIDTH + 10)

        # labels = ["Position", "Name", "Duration (ms)", "Record Data"]
        
        # for label in labels:
            # labelWidget = QLabel(label)
            # labelWidget.setFixedWidth(WIDTH)
            # labelWidget.setFixedHeight(HEIGHT)
            # self.layout().addWidget(labelWidget)
            
        # outputLabels = ["Start (Hz)", "End (Hz)", "Duty Cycle (%)"]
        # excitationLabels = ["Amplitude", "Phase (deg)"]
        
        # for output in range(3):
            # line = QFrame()
            # line.setFrameShape(QFrame.HLine)
            # self.layout().addWidget(line)
            # for label in outputLabels:
                # labelWidget = QLabel(label)
                # labelWidget.setFixedWidth(WIDTH)
                # labelWidget.setFixedHeight(HEIGHT)
                # self.layout().addWidget(labelWidget)
            # for label in excitationLabels:
                # labelWidget = QLabel(label)
                # labelWidget.setFixedWidth(WIDTH)
                # labelWidget.setFixedHeight(HEIGHT)
                # self.layout().addWidget(labelWidget)
            

        # Create table for analog outputs
        # self.analog_table = QTableWidget(ANALOG_ROWS, 1)
        # self.layout().addWidget(self.analog_table)
        # Set up sizes and hide default headers
        # self.analog_table.horizontalHeader().hide()
        # self.analog_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        # self.analog_table.setFixedWidth(WIDTH+2)
        # self.analog_table.verticalHeader().hide()
        # self.analog_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        # self.analog_table.setFixedHeight(HEIGHT*ANALOG_ROWS+2)

        # Create table for digital outputs
        # self.digital_table = QTableWidget(DIGITAL_ROWS, 1)
        # self.layout().addWidget(self.digital_table)
        # Set up sizes and hide default headers
        # self.digital_table.horizontalHeader().hide()
        # self.digital_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        # self.digital_table.setFixedWidth(WIDTH+2)
        # self.digital_table.verticalHeader().hide()
        # self.digital_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        # self.digital_table.setFixedHeight(HEIGHT*DIGITAL_ROWS+2)

class ScanFunctionSegment(list):
    # Signal for updating plot
    is_changed = pyqtSignal()

    def __init__(self, analog_labels, digital_labels):
        super(ScanFunctionSegment, self).__init__()
        
        self.build_segment()
        
    def build_segment(self):
        self.append(QLabel())
        self.append(QLineEdit())
        self.append(QLineEdit())
        self.append(QComboBox())
        for i in range(NUM_OUTPUTS):
            self.append(QFrame())
            self.append(QLabel("asdf"))
            self.append(QLineEdit())
            self.append(QLineEdit())
            self.append(QLineEdit())
            self.append(QComboBox())
            self.append(QLineEdit())
            self.append(QLineEdit())
        self.append(QTableWidget(ANALOG_ROWS, 1))
        self.append(QTableWidget(DIGITAL_ROWS, 1))
    
        # Create layout for segment
        # self.segment_layout = QVBoxLayout()
        # self.setLayout(self.segment_layout)
        # self.setFixedWidth(WIDTH*2+10)

        # Show position number
        # self.position_label = QLabel()
        # self.position_label.setAlignment(Qt.AlignCenter)
        # self.segment_layout.addWidget(self.position_label)

        # Create label and box for name
        # self.name_label = QLabel("Name")
        # self.name_box = QLineEdit()
        # self.name_label.setFixedWidth(WIDTH)
        # self.name_box.setFixedWidth(WIDTH)
        # self.name_layout = QHBoxLayout()
        # self.name_layout.addWidget(self.name_label)
        # self.name_layout.addWidget(self.name_box)
        # self.segment_layout.addLayout(self.name_layout)

        # Create label and box for duration
        # self.duration_label = QLabel("Duration (ms)")
        # self.duration_box = QLineEdit("0")
        # self.duration_label.setFixedWidth(WIDTH)
        # self.duration_box.setFixedWidth(WIDTH)
        # self.duration_box.textChanged.connect(self.isChanged)
        # self.duration_layout = QHBoxLayout()
        # self.duration_layout.addWidget(self.duration_label)
        # self.duration_layout.addWidget(self.duration_box)
        # self.segment_layout.addLayout(self.duration_layout)

        # Create label and box for choosing to record data
        # self.data_record_label = QLabel("Record data")
        # self.data_record_box = QComboBox()
        # self.data_record_box.addItem("False")
        # self.data_record_box.addItem("True")
        # self.data_record_box.currentTextChanged.connect(self.colorDataRecordBox)
        # self.data_record_label.setFixedWidth(WIDTH)
        # self.data_record_box.setFixedWidth(WIDTH)
        # self.data_record_layout = QHBoxLayout()
        # self.data_record_layout.addWidget(self.data_record_label)
        # self.data_record_layout.addWidget(self.data_record_box)
        # self.segment_layout.addLayout(self.data_record_layout)

        # Create Output sections
        # self.output_list = []
        # for output in range(3):
            # self.output_list.append(OutputParameterLayout(output))
            # self.segment_layout.addLayout(self.output_list[output])
            # for name, [label, parameter] in self.output_list[output].parameter_dict.items():
                # try:
                    # parameter.textChanged.connect(self.isChanged)
                # except:
                    # parameter.currentTextChanged.connect(self.isChanged)

        # Create table for analog outputs
        # self.analog_table = QTableWidget(ANALOG_ROWS, 2)
        # Add table to layout
        # self.segment_layout.addWidget(self.analog_table)
        # Set up sizes and hide default headers
        # self.analog_table.horizontalHeader().hide()
        # self.analog_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        # self.analog_table.setFixedWidth(WIDTH*2+2)
        # self.analog_table.verticalHeader().hide()
        # self.analog_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        # self.analog_table.setFixedHeight(HEIGHT*ANALOG_ROWS+2)
        # Set up labels
        # for row in range(ANALOG_ROWS):
            # self.analog_table.setItem(row, 0, QTableWidgetItem(analog_labels[row]))
            # self.analog_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        # Set up boxes
        # for row in range(ANALOG_ROWS):
            # self.analog_table.setCellWidget(row, 1, QLineEdit("0"))

        # Create table for digital outputs
        # self.digital_table = QTableWidget(DIGITAL_ROWS, 2)
        # Add table to layout
        # self.segment_layout.addWidget(self.digital_table)
        # Set up sizes and hide default headers
        # self.digital_table.horizontalHeader().hide()
        # self.digital_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        # self.digital_table.setFixedWidth(WIDTH*2+2)
        # self.digital_table.verticalHeader().hide()
        # self.digital_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        # self.digital_table.setFixedHeight(HEIGHT*DIGITAL_ROWS+2)
        # Set up labels
        # for row in range(DIGITAL_ROWS):
            # self.digital_table.setItem(row, 0, QTableWidgetItem(digital_labels[row]))
            # self.digital_table.item(row, 0).setFlags(Qt.ItemIsSelectable)
        # Set up boxes
        # for row in range(DIGITAL_ROWS):
            # self.digital_box = QComboBox()
            # self.digital_box.addItem("False")
            # self.digital_box.addItem("True")
            # self.digital_table.setCellWidget(row, 1, self.digital_box)
            # self.digital_table.cellWidget(row, 1).currentTextChanged.connect(self.colorDigitalBox)

    def update_position(self, position):
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

class ScanWidget(QSplitter):
    def __init__(self, textWidget):
        super(ScanWidget, self).__init__(Qt.Vertical)
        
        self.textWidget = textWidget
        self.scanFunction = ScanFunction()
        
        self.scanArea = ScanArea(self.scanFunction)
        # self.scanPlot = ScanPlot(self.scanFunction)
        
        self.build_widget()
        # self.signal_handler()
        
    def build_widget(self):
        self.addWidget(self.scanArea)
        # self.addWidget(self.scanPlot)
        
    # def signal_handler(self):
        # self.scanArea.headerView.model().dataChanged.connect(lambda: self.scanPlot.update(self.scanFunction))
        # for i in range(self.scanArea.OUTPUTS):
            # self.scanArea.outputViewList[i].model().dataChanged.connect(self.scanPlot.update)
        # self.scanArea.analogView.model().dataChanged.connect(self.scanPlot.update)
        # self.scanArea.digitalView.model().dataChanged.connect(self.scanPlot.update)
        
    def save_check(self):
        msgBox = QMessageBox()
        msgBox.setText("Do you want to save the current scan?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return msgBox.exec()
        
    def save_scan(self):
        fileName = QFileDialog.getSaveFileName(filter='Scan Files (*.scan);;Text Files (*.txt)')[0]
        file = open(fileName, 'w')
        file.write(json.dumps(self.scanFunction, sort_keys=False, indent=4))
        file.close()
        
        scanPic = self.scanArea.widget().grab()
        scanPicFileName = fileName.replace('.scan', '.jpg')
        scanPic.save(scanPicFileName, 'jpg')
        
    def open_scan(self):
        choice = self.save_check()
        if choice == QMessageBox.Cancel:
            pass
        else:
            if choice == QMessageBox.Yes:
                self.save_scan()
                
            fileName = QFileDialog.getOpenFileName(filter='Scan Files (*.scan);;Text Files (*.txt);;All Files (*.*)')[0]
            
            try:
                file = open(fileName, 'r')
                scanData = file.read()
                
                newScanFunction = json.loads(scanData)
                self.scanArea.reset(len(newScanFunction))
                self.scanFunction.reset(newScanFunction)
                
            except:
                self.textWidget.appendPlainText("File open failed")
        
class ScanArea(QScrollArea):
    def __init__(self, scanFunction):
        super(ScanArea, self).__init__()
        
        self.headerLabels = ["Name", "Active", "Record", "Duration"]
        self.headerTypes = [str, Bool, Bool, PosFloat]
        self.OUTPUTS = 3
        self.outputLabels = ["Start", "End", "Duty Cycle", "Tickle", "Amplitude", "Phase"]
        self.outputTypes = [FreqFloat, FreqFloat, DCFloat, DivChoice, AmpFloat, Bool]
        self.ANALOG = 8
        self.analogLabels = ["A" + str(i + 1) for i in range(self.ANALOG)]
        self.analogTypes = [RangedFloat for i in range(self.ANALOG)]
        self.DIGITAL = 12
        self.digitalLabels = ["D" + str(i + 1) for i in range(self.DIGITAL)]
        self.digitalTypes = [Bool for i in range(self.DIGITAL)]
        
        self.build_widget(scanFunction)
        
    def build_widget(self, scanFunction):
        self.setWidget(QWidget())
        self.setWidgetResizable(True)
        self.widget().setLayout(QGridLayout())
        self.widget().layout().setAlignment(Qt.AlignLeft)
        
        self.headerView = ParameterView()
        self.headerView.setupModel(HeaderModel(scanFunction, self.headerLabels, self.headerTypes))
        self.outputViewList = []
        for i in range(self.OUTPUTS):
            self.outputViewList.append(ParameterView())
            self.outputViewList[i].setupModel(OutputModel(scanFunction, i, self.outputLabels, self.outputTypes))
        self.analogView = ParameterView()
        self.analogView.setupModel(ListParsModel(scanFunction, "Analog", self.analogLabels, self.analogTypes))
        self.digitalView = ParameterView()
        self.digitalView.setupModel(ListParsModel(scanFunction, "Digital", self.digitalLabels, self.digitalTypes))
        
        self.widget().layout().addWidget(self.headerView)
        for i in range(NUM_OUTPUTS):
            self.widget().layout().addWidget(self.outputViewList[i])
        self.widget().layout().addWidget(self.analogView)
        self.widget().layout().addWidget(self.digitalView)
                
    def reset(self, newLength):
        while self.remove_segment(0):
            None
        for i in range(newLength):
            self.add_segment(i)
        
    def add_segment(self, position):
        self.headerView.model().insertColumn(position, QModelIndex())
        for i in range(NUM_OUTPUTS):
            self.outputViewList[i].model().insertColumn(position, QModelIndex())
        self.analogView.model().insertColumn(position, QModelIndex())
        self.digitalView.model().insertColumn(position, QModelIndex())
        
    def remove_segment(self, position):
        if self.headerView.model().removeColumn(position, QModelIndex()):
            for i in range(NUM_OUTPUTS):
                self.outputViewList[i].model().removeColumn(position, QModelIndex())
            self.analogView.model().removeColumn(position, QModelIndex())
            self.digitalView.model().removeColumn(position, QModelIndex())
            return True
        else:
            return False
        
class ParameterView(QTableView):
    def __init__(self):
        super(ParameterView, self).__init__()
    
    def setupModel(self, model):
        self.setModel(model)
        self.verticalHeader().setFixedWidth(100)
        self.setFixedSize(self.horizontalHeader().length() + self.verticalHeader().width() + 2, self.horizontalHeader().height() + self.verticalHeader().length() + 2)
        self.model().columnsInserted.connect(lambda: self.setFixedSize(self.horizontalHeader().length() + self.verticalHeader().width() + 2, self.horizontalHeader().height() + self.verticalHeader().length() + 2))
        self.model().columnsRemoved.connect(lambda: self.setFixedSize(self.horizontalHeader().length() + self.verticalHeader().width() + 2, self.horizontalHeader().height() + self.verticalHeader().length() + 2))
        
class ParameterModel(QAbstractTableModel):
    def __init__(self, scanFunction, labels, types):
        super(ParameterModel, self).__init__()
        
        self.scanFunction = scanFunction
        
        self.labels = labels
        self.types = types
        
    def rowCount(self, parent):
        return len(self.labels)
        
    def columnCount(self, parent):
        return(len(self.scanFunction))
        
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole:
            if orientation == Qt.Vertical:
                return self.labels[section]
            else:
                return section + 1
        
    def check_data_type(self, value, type):
        try:
            v = type(value)
        except:
            v = ""
        return v
        
    def flags(self, index):
        return Qt.ItemIsEditable | QAbstractTableModel.flags(self, index)
        
class HeaderModel(ParameterModel):
    def __init__(self, scanFunction, labels, types):
        super(HeaderModel, self).__init__(scanFunction, labels, types)
                                
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.scanFunction[index.column()][self.labels[index.row()]])
                    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # v = self.check_data_type(value, self.types[index.row()])
            self.scanFunction[index.column()][self.labels[index.row()]] = self.types[index.row()](value)
            self.dataChanged.emit(index, index)
        return True
        
    def insertColumn(self, position, parent):
        if position <= len(self.scanFunction) and position >= 0:
            self.beginInsertColumns(parent, position, position)
            self.scanFunction.insert(position, OrderedDict())
            for label, type in zip(self.labels, self.types):
                if position > 0:
                    self.scanFunction[position][label] = self.scanFunction[position - 1][label]
                else:
                    self.scanFunction[position][label] = type(0)
            self.scanFunction[position]["Outputs"] = []
            self.endInsertColumns()
            return True
        else:
            return False
            
    def removeColumn(self, position, parent):
        if position < len(self.scanFunction) and position >= 0:
            self.beginRemoveColumns(parent, position, position)
            self.scanFunction.remove(self.scanFunction[position])
            self.endRemoveColumns()
            return True
        else:
            return False
                
class OutputModel(ParameterModel):
    def __init__(self, scanFunction, output, labels, types):
        super(OutputModel, self).__init__(scanFunction, labels, types)
        
        self.output = output
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.scanFunction[index.column()]["Outputs"][self.output][self.labels[index.row()]])
        if role == Qt.ToolTipRole and self.labels[index.row()] == "Tickle":
            return "Div / [value here] or Output 3"
        
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # v = self.check_data_type(value, self.types[index.row()])
            self.scanFunction[index.column()]["Outputs"][self.output][self.labels[index.row()]] = self.types[index.row()](value)
            self.dataChanged.emit(index, index)
        return True
        
    def insertColumn(self, position, parent):
        if position <= len(self.scanFunction) and position >= 0:
            self.beginInsertColumns(parent, position, position)
            self.scanFunction[position]["Outputs"].append(OrderedDict())
            for label, type in zip(self.labels, self.types):
                if position > 0:
                    self.scanFunction[position]["Outputs"][self.output][label] = self.scanFunction[position - 1]["Outputs"][self.output][label]
                else:
                    self.scanFunction[position]["Outputs"][self.output][label] = type(0)
            self.endInsertColumns()
            return True
        else:
            return False
            
    def removeColumn(self, position, parent):
        self.beginRemoveColumns(parent, position, position)
        self.endRemoveColumns()
       
class ListParsModel(ParameterModel):
    def __init__(self, scanFunction, name, labels, types):
        super(ListParsModel, self).__init__(scanFunction, labels, types)
        
        self.name = name
        
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.scanFunction[index.column()][self.name][index.row()])
        
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # v = self.check_data_type(value, self.types[index.row()])
            self.scanFunction[index.column()][self.name][index.row()] = self.types[index.row()](value)
            self.dataChanged.emit(index, index)
        return True
        
    def insertColumn(self, position, parent):
        if position <= len(self.scanFunction) and position >= 0:
            self.beginInsertColumns(parent, position, position)
            self.scanFunction[position][self.name] = []
            for i in range(len(self.labels)):
                if position > 0:
                    self.scanFunction[position][self.name].append(self.scanFunction[position - 1][self.name][i])
                else:
                    self.scanFunction[position][self.name].append(self.types[i](0))
            self.endInsertColumns()
            return True
        else:
            return False
            
    def removeColumn(self, position, parent):
        self.beginRemoveColumns(parent, position, position)
        self.endRemoveColumns()

class ScanPlot(pg.PlotWidget):
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

class RangedFloat(float):
    def __new__(cls, value):
        try:
            v = float.__new__(cls, min(max(-10, float(value)), 10))
        except ValueError:
            v = 0
        return v
        
class FreqFloat(float):
    def __new__(cls, value):
        try:
            v = float.__new__(cls, min(max(0, float(value)), 500000))
        except ValueError:
            v = 0
        return v
        
class DCFloat(float):
    def __new__(cls, value):
        try:
            v = float.__new__(cls, min(max(0, float(value)), 100))
        except ValueError:
            v = 0
        return v
        
class AmpFloat(float):
    def __new__(cls, value):
        try:
            v = float.__new__(cls, min(max(0, float(value)), 5))
        except ValueError:
            v = 0
        return v
        
class PosFloat(float):
    def __new__(cls, value):
        try:
            v = float.__new__(cls, max(0, float(value)))
        except ValueError:
            v = 0
        return v
        
class Bool(int):
    def __new__(cls, value):
        try:
            s = int.__new__(cls, bool(int(value)))
        except ValueError:
            s = 0
        l = ["False", "True"]
        return l[s]
        
class DivChoice(str):
    def __new__(cls, value):
        try:
            v = int(value)
            if v == 2 or v == 4 or v == 8 or v == 16:
                s = str.__new__(cls, "Div / " + str(v))
            else:
                raise ValueError()
        except ValueError:
            s = "Output 3"
        return s