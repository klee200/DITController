from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from Communication import SerialPort
from ScanFunction import *
import pdb

class OpenScanDialog(QFileDialog):
    def __init__(self, main_window):
        super(OpenScanDialog, self).__init__()
        try:
            # Make sure mode is set to frequency
            if main_window.mass_button.isChecked() == True:
                main_window.frequency_button.setChecked(True)
            # Get file name from text box
            self.file_name = self.getOpenFileName(filter='Scan Files (*.mcl);;Text Files (*.txt)')[0]
            # Open file for reading
            self.file = open(self.file_name, 'r')
            # Read data from file
            self.scan_funciton_data = self.file.read()
            # Generate scan function from read data
            main_window.scan_function.convertFromJson(self.scan_funciton_data)
        except:
            pass

class SaveScanDialog(QFileDialog):
    def __init__(self, main_window):
        super(SaveScanDialog, self).__init__()
        try:
            # Make sure mode is set to frequency
            if main_window.mass_button.isChecked() == True:
                main_window.frequency_button.setChecked(True)
            # Get file name from text box
            self.file_name = self.getSaveFileName(filter='Scan Files (*.mcl);;Text Files (*.txt)')[0]
            # Create file for writing
            self.file = open(self.file_name, 'w')
            # Write json to file
            self.file.write(main_window.scan_function.convertToJson())
            self.file.close()
        except:
            pass

class ConnectionDialog(QDialog):
    def __init__(self, announcer):
        super(ConnectionDialog, self).__init__()
        # Create layout for dialog box
        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)
        # Create labels
        self.master_label = QLabel('Master: ')
        self.main_layout.addWidget(self.master_label, 0, 0)
        self.slave_label = QLabel('Slave: ')
        self.main_layout.addWidget(self.slave_label, 3, 0)
        # Create boxes
        self.master_box = QLineEdit()
        self.main_layout.addWidget(self.master_box, 0, 1)
        self.slave_box = QLineEdit()
        self.main_layout.addWidget(self.slave_box, 3, 1)
        # Create buttons
        self.master_connect_button = QPushButton('Connect Master')
        self.main_layout.addWidget(self.master_connect_button, 1, 0)
        self.master_disconnect_button = QPushButton('Disconnect Master')
        self.main_layout.addWidget(self.master_disconnect_button, 1, 1)
        self.slave_connect_button = QPushButton('Connect Slave')
        self.main_layout.addWidget(self.slave_connect_button, 4, 0)
        self.slave_disconnect_button = QPushButton('Disconnect Slave')
        self.main_layout.addWidget(self.slave_disconnect_button, 4, 1)
        # Button functions
        self.master_connect_button.clicked.connect(lambda: self.connectMaster(self.master_box.text()))
        self.master_disconnect_button.clicked.connect(self.disconnectMaster)
        # self.slave_connect_button.clicked.connect(self.connectSlave)
        # self.slave_disconnect_button.clicked.connect(self.disconnectSlave)
        # Create line
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.main_layout.addWidget(self.line, 2, 0, 1, 2)

        # Allow external dialog to access announcer in Main Window
        self.announcer = announcer

    def connectMaster(self, port_choice):
        try:
            self.master_serial = SerialPort(port_choice, self.announcer)
            self.announcer.appendPlainText("Master serial connected")
        except:
            self.announcer.appendPlainText("No serial port found")

    def disconnectMaster(self):
        try:
            self.master_serial.close()
            self.master_serial = None
            self.announcer.appendPlainText("Master serial disconnected")
        except:
            self.announcer.appendPlainText("No connection found")

class AddRemoveSegmentDialog(QDialog):
    def __init__(self, main_window):
        super(AddRemoveSegmentDialog, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # Create layout
        self.setLayout(QGridLayout())
        # Create labels and boxes
        self.layout().addWidget(QLabel("Insert new segment at position:"), 1, 0)
        self.add_position_box = QLineEdit()
        self.layout().addWidget(self.add_position_box, 1, 1)
        self.layout().addWidget(QLabel("Remove segment from position:"), 3, 0)
        self.remove_position_box = QLineEdit()
        self.layout().addWidget(self.remove_position_box, 3, 1)
        # Create buttons
        self.insert_seg_button = QPushButton("Insert segment")
        self.layout().addWidget(self.insert_seg_button, 2, 0, 1, 2)
        self.remove_seg_button = QPushButton("Remove segment")
        self.layout().addWidget(self.remove_seg_button, 4, 0, 1, 2)
        self.close_button = QPushButton("Close")
        self.layout().addWidget(self.close_button, 5, 0, 1, 2)
        # Button functions
        self.insert_seg_button.clicked.connect(lambda: self.insertScanSegment(main_window))
        self.remove_seg_button.clicked.connect(lambda: self.removeScanSegment(main_window))
        self.close_button.clicked.connect(self.close)

    def insertScanSegment(self, main_window):
        # Calculate position to insert at
        try:
            self.position = int(self.add_position_box.text())-1
        except:
            self.position = len(main_window.scan_function.scan_list)

        main_window.scan_function.addSegment(self.position)

    def removeScanSegment(self, main_window):
        # Calculate position to remove from
        try:
            self.position = int(self.remove_position_box.text())-1
        except:
            self.position = len(main_window.scan_function.scan_list)-1

        main_window.scan_function.removeSegment(self.position)

class CopySegmentDialog(QDialog):
    def __init__(self, main_window):
        super(CopySegmentDialog, self).__init__()
        # Set layout
        self.setLayout(QGridLayout())
        # Add labels and boxes
        self.layout().addWidget(QLabel("Copy segment:"), 0, 0)
        self.copy_box = QLineEdit()
        self.layout().addWidget(self.copy_box, 0, 1)
        self.layout().addWidget(QLabel("to:"), 1, 0)
        self.paste_box = QLineEdit()
        self.layout().addWidget(self.paste_box, 1, 1)
        # Add buttons
        self.copy_button = QPushButton("Do it")
        self.layout().addWidget(self.copy_button)
        self.copy_button.clicked.connect(lambda: self.copyAndPaste(main_window, int(self.copy_box.text())-1, int(self.paste_box.text())-1))

    def copyAndPaste(self, main_window, copy_position, paste_position):
        # Create new segment at paste position
        new_segment = main_window.scan_function.addSegment(paste_position)
        # Copy parameters from copy position
        new_segment.convertFromDictionary(main_window.scan_function.scan_list[copy_position].convertToDictionary())

class EditAnaDigLabelsDialog(QDialog):
    def __init__(self, main_window):
        super(EditAnaDigLabelsDialog, self).__init__()
        # List that holds labels
        self.analog_labels = []
        self.digital_labels = []
        # Make layout
        self.setLayout(QGridLayout())
        # Create two tables
        self.analog_table = QTableWidget(ANALOG_ROWS, 1)
        self.analog_table.horizontalHeader().hide()
        self.analog_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.analog_table.setFixedWidth(WIDTH+2)
        self.analog_table.verticalHeader().hide()
        self.analog_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.layout().addWidget(self.analog_table, 0, 0)
        self.digital_table = QTableWidget(DIGITAL_ROWS, 1)
        self.digital_table.horizontalHeader().hide()
        self.digital_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.digital_table.setFixedWidth(WIDTH+2)
        self.digital_table.verticalHeader().hide()
        self.digital_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.layout().addWidget(self.digital_table, 0, 1)
        # Create buttons
        self.ok_button = QPushButton("Ok")
        self.layout().addWidget(self.ok_button, 1, 0)
        self.cancel_button = QPushButton("Cancel")
        self.layout().addWidget(self.cancel_button, 1, 1)
        # Button functions
        self.ok_button.clicked.connect(lambda: self.updateAnaDigLabels(main_window))
        self.cancel_button.clicked.connect(self.close)
        # Pull names from scan function labels
        for row in range(ANALOG_ROWS):
            self.analog_table.setItem(row, 0, QTableWidgetItem(main_window.scan_function.analog_labels[row]))
        for row in range(DIGITAL_ROWS):
            self.digital_table.setItem(row, 0, QTableWidgetItem(main_window.scan_function.digital_labels[row]))

    def updateAnaDigLabels(self, main_window):
        for row in range(ANALOG_ROWS):
            self.analog_labels.append(self.analog_table.item(row, 0).text())
        for row in range(DIGITAL_ROWS):
            self.digital_labels.append(self.digital_table.item(row, 0).text())
        main_window.scan_function.updateLabels(self.analog_labels, self.digital_labels)
        self.close()
