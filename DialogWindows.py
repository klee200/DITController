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

class CalculatorDialog(QDialog):
    def __init__(self, main_window):
        super(CalculatorDialog, self).__init__()
        # Make layout
        self.setLayout(QGridLayout())
        # Make labels and boxes
        self.layout().addWidget(QLabel("r\u2080 (cm)"), 0, 0)
        self.r_box = QLineEdit("1.0")
        self.layout().addWidget(self.r_box, 0, 1)
        self.layout().addWidget(QLabel("z\u2080 (cm)"), 1, 0)
        self.z_box = QLineEdit("0.707")
        self.layout().addWidget(self.z_box, 1, 1)
        self.layout().addWidget(QLabel("High V (V)"), 0, 2)
        self.high_v_box = QLineEdit("500")
        self.layout().addWidget(self.high_v_box, 0, 3)
        self.layout().addWidget(QLabel("Low V (V)"), 1, 2)
        self.low_v_box = QLineEdit("-500")
        self.layout().addWidget(self.low_v_box, 1, 3)
        self.layout().addWidget(QLabel("Duty Cycle (0 - 1)"), 2, 2)
        self.d_box = QLineEdit("0.5")
        self.layout().addWidget(self.d_box, 2, 3)
        self.layout().addWidget(QLabel("a"), 0, 4)
        self.a_z_box = QLineEdit("0")
        self.layout().addWidget(self.a_z_box, 0, 5)
        self.layout().addWidget(QLabel("q"), 1, 4)
        self.q_z_box = QLineEdit("0.712")
        self.layout().addWidget(self.q_z_box, 1, 5)
        # Make horizontal line
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.layout().addWidget(self.line, 3, 0, 1, 6)
        # Make m/z and frequency boxes
        self.layout().addWidget(QLabel("Frequency (Hz)"), 4, 0)
        self.frequency_box = QLineEdit()
        self.layout().addWidget(self.frequency_box, 4, 1)
        self.layout().addWidget(QLabel("m/z"), 4, 2)
        self.mass_box = QLineEdit()
        self.layout().addWidget(self.mass_box, 4, 3)
        # Make conversion constant box
        self.layout().addWidget(QLabel("Conversion constant"), 4, 4)
        self.conv_const_box = QLineEdit()
        self.layout().addWidget(self.conv_const_box, 4, 5)
        self.button = QPushButton("Copy constant")
        self.layout().addWidget(self.button, 5, 5)
        self.button.clicked.connect(lambda: main_window.conv_const_box.setText(self.conv_const_box.text()))

        # Connect az and qz boxes
        # self.a_z_box.textEdited.connect(self.calculateQz)
        self.q_z_box.textEdited.connect(self.calculateAz)
        self.q_z_box.textEdited.connect(self.calculateConvConstant)
        # Connect frequency and m/z boxes
        self.frequency_box.textEdited.connect(self.calculateMass)
        self.mass_box.textEdited.connect(self.calculateFrequency)

    def calculateQz(self, a_z):
        # Calculate U and V
        try:
            U = float(self.d_box.text()) * float(self.high_v_box.text()) + (1 - float(self.d_box.text())) * float(self.low_v_box.text())
            V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())) * float(self.d_box.text())
            q_z = str(-1 * float(a_z) * V / 2 / U)
        except:
            q_z = None

        self.q_z_box.setText(q_z)

    def calculateAz(self, q_z):
        # Calculate U and V
        try:
            U = float(self.d_box.text()) * float(self.high_v_box.text()) + (1 - float(self.d_box.text())) * float(self.low_v_box.text())
            V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())) * float(self.d_box.text())
            a_z = str(-1 * float(q_z) * 2* U / V)
        except:
            a_z = None

        self.a_z_box.setText(a_z)

    def calculateMass(self, frequency):
        # m/z = 8*e*V/(r^2+2z^2)/frequency^2/qz
        try:
            V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())) * float(self.d_box.text())
            mass = str(8 * 1.602e-19 * V / (pow(float(self.r_box.text())/100, 2) + 2 * pow(float(self.z_box.text())/100, 2)) / pow(float(frequency)*2*pi, 2) / float(self.q_z_box.text()) / 1.66e-27)
        except:
            mass = None

        self.mass_box.setText(mass)

    def calculateFrequency(self, mass):
        try:
            V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())) * float(self.d_box.text())
            frequency = str(sqrt(8 * 1.602e-19 * V / (pow(float(self.r_box.text())/100, 2) + 2 * pow(float(self.z_box.text())/100, 2)) / float(mass) / float(self.q_z_box.text()) / 1.66e-27)/2/pi)
        except:
            frequency = None

        self.frequency_box.setText(frequency)

    def calculateConvConstant(self, q_z):
        try:
            V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())) * float(self.d_box.text())
            constant = str((8 * 1.602e-19 * V / (pow(float(self.r_box.text())/100, 2) + 2 * pow(float(self.z_box.text())/100, 2)) / float(q_z) / 1.66e-27)/pow(2*pi, 2))
        except:
            constant = None

        self.conv_const_box.setText(constant)
