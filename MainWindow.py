import pdb
import serial
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ScanFunction import *
from Communication import *
from DialogWindows import *

class MainWindow(QMainWindow):
    def __init__(self):
        # Call parent constructor
        super(MainWindow, self).__init__()

        # Create scan function object
        self.scan_function = ScanFunction(self)

        # Create splitter for left and right halves and make it the central widget
        self.main_splitter = QSplitter()
        self.main_splitter.setContentsMargins(10,10,10,10)
        self.setCentralWidget(self.main_splitter)

        # Left half of main layout has two vertically stacked sections
        self.left_splitter = QSplitter()
        self.left_splitter.setOrientation(Qt.Vertical)
        # Add left half to main splitter
        self.main_splitter.addWidget(self.left_splitter)

        # Right half of main layout has two vertically stacked sections
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0,0,0,0)
        self.right_half = QWidget()
        self.right_half.setLayout(self.right_layout)
        # Add right half to main splitter
        self.main_splitter.addWidget(self.right_half)

        # Make left half as large as possible
        self.main_splitter.setSizes([1, 0])

        # Top left displays scan sections
        # Each output is displayed on a different tab
        self.scan_area = QScrollArea()
        # Create output 1 area for tab 1
        self.scan_area.setWidget(QWidget())
        self.scan_area.setWidgetResizable(True)
        self.scan_area.widget().setLayout(QHBoxLayout())
        self.scan_area.widget().layout().setAlignment(Qt.AlignLeft)
        # Add scan area to left splitter
        self.left_splitter.addWidget(self.scan_area)

        # Bottom left displays plot of scan sections
        # Add plot to left half and hides it
        self.left_splitter.addWidget(self.scan_function.scan_plot)
        self.scan_function.scan_plot.hide()

        # Top right displays buttons in grid layout
        self.button_layout = QGridLayout()
        # Add button layout to right half
        self.right_layout.addLayout(self.button_layout)
        # Create buttons at locations (row, column) in grid
        # Select frequency or m/z display
        self.frequency_button = QRadioButton("Frequency")
        self.button_layout.addWidget(self.frequency_button, 0, 0)
        self.mass_button = QRadioButton("m/z")
        self.button_layout.addWidget(self.mass_button, 0, 1)
        self.convert_buttons = QButtonGroup()
        self.convert_buttons.addButton(self.frequency_button)
        self.convert_buttons.addButton(self.mass_button)
        # Initial state
        self.frequency_button.setChecked(True)
        self.mass_button.setCheckable(False)
        # Display select functions
        self.frequency_button.toggled.connect(lambda: self.convertNumbers(self.conv_const_box.text()))
        # Create label and box for conversion constant
        self.button_layout.addWidget(QLabel("Conversion constant"), 1, 0)
        self.conv_const_box = QLineEdit()
        self.button_layout.addWidget(self.conv_const_box, 1, 1)
        self.conv_const_box.textChanged.connect(self.setConversionState)
        # Add scan segment button
        self.add_remove_button = QPushButton("Add/Remove Segments")
        self.button_layout.addWidget(self.add_remove_button, 2, 0, 1, 2)
        # Add/remove scan segment button function
        self.add_remove_button.clicked.connect(lambda: AddRemoveSegmentDialog(self).open())
        # Download button
        self.download_button = QPushButton("Download Scan")
        self.button_layout.addWidget(self.download_button, 3, 0)
        # Download button function
        self.download_button.clicked.connect(self.downloadScanFunction)
        # Upload button
        self.upload_button = QPushButton("Upload Scan")
        self.button_layout.addWidget(self.upload_button, 3, 1)
        # Upload button function
        self.upload_button.clicked.connect(self.uploadScanFunction)
        # Run button
        self.run_button = QPushButton("Run Scan")
        self.button_layout.addWidget(self.run_button, 4, 0)
        # Run button function
        self.run_button.clicked.connect(self.runScanFunction)
        # Stop button
        self.stop_button = QPushButton("Stop Scan")
        self.button_layout.addWidget(self.stop_button, 4, 1)
        # Stop button function
        self.stop_button.clicked.connect(self.stopScanFunction)

        # Bottom right displays announcer
        self.announcer = QPlainTextEdit()
        self.announcer.setReadOnly(True)
        # Add announcer to right half
        self.right_layout.addWidget(self.announcer)

        # Create menu
        self.menuBar()

        # File menu
        self.file_menu = self.menuBar().addMenu("File")
        # Open scan option
        self.open_option = self.file_menu.addAction("Open Scan")
        self.open_option.triggered.connect(lambda: OpenScanDialog(self))
        # Save scan option
        self.save_option = self.file_menu.addAction("Save Scan")
        self.save_option.triggered.connect(lambda: SaveScanDialog(self))

        # Edit menu
        self.edit_menu = self.menuBar().addMenu("Edit")
        # Add/remove option
        self.add_remove_option = self.edit_menu.addAction("Add/Remove segments")
        self.add_remove_option.triggered.connect(lambda: AddRemoveSegmentDialog(self).open())
        # Copy segment option
        self.copy_option = self.edit_menu.addAction("Copy segment")
        self.copy_dialog = CopySegmentDialog(self)
        self.copy_option.triggered.connect(self.copy_dialog.show)
        # Edit analog and digital labels
        self.labels_option = self.edit_menu.addAction("Edit labels")
        self.labels_option.triggered.connect(lambda: EditAnaDigLabelsDialog(self).exec())
        # Edit conversion constant
        self.calculator_option = self.edit_menu.addAction("Calculator")
        self.calculator_option.triggered.connect(lambda: CalculatorDialog(self).open())

        # Settings menu
        self.settings_menu = self.menuBar().addMenu("Settings")
        self.connection_option = self.settings_menu.addAction("Connect")
        # Create connection dialog box
        self.connection_dialog = ConnectionDialog(self.announcer)
        # Show dialog box when button is clicked
        self.connection_option.triggered.connect(self.connection_dialog.exec)

    def setConversionState(self, constant):
        try:
            # If constant box has a number allow user to push conversion buttons
            float(constant)
            self.frequency_button.setCheckable(True)
            self.mass_button.setCheckable(True)
        except:
            # Otherwise the user cannot push buttons (based on which is already pushed)
            if self.frequency_button.isChecked():
                self.mass_button.setCheckable(False)
            else:
                self.frequency_button.setCheckable(False)

    def convertNumbers(self, conversion_constant):
        if self.frequency_button.isChecked() == True:
            self.scan_function.convertToFrequency(conversion_constant)
        elif self.mass_button.isChecked() == True:
            self.scan_function.convertToMass(conversion_constant)

    def downloadScanFunction(self):
        # Check validity of scan function
        self.valid_scan_function = True
        # Count the number of mass analysis steps total
        self.num_mass_anaylsis_segments = 0
        for segment in self.scan_function.scan_list:
            # Count the number of ramp outputs in each segment
            self.num_ramps = 0
            for output in segment.output_list:
                if output.parameter_dict["Type"][1].currentText() == "Mass Analysis":
                    self.num_mass_anaylsis_segments += 1
                if output.parameter_dict["Type"][1].currentText() in ["Ramp", "Mass Analysis", "Isolation"]:
                    self.num_ramps += 1
            # Count the number of output 3 special functions
            self.num_special = 0
            for output in segment.output_list:
                if output.parameter_dict["Type"][1].currentText() in ["CID", "Isolation"]:
                    self.num_special += 1
            # If more than one ramp segment found, the scan function is invalid
            if self.num_ramps > 1 or self.num_special > 1:
                self.valid_scan_function = False
        # Only one allowed mass analysis step in scan function
        if self.num_mass_anaylsis_segments > 1:
            self.valid_scan_function = False

        if self.valid_scan_function == False:
            self.announcer.appendPlainText("Invalid scan function")
        else:
            # Make sure that numbers are in frequency for download
            if self.mass_button.isChecked() == True:
                self.frequency_button.toggle()
            # Convert list into json string
            scan_function_json = self.scan_function.convertToJson()
            self.announcer.appendPlainText(scan_function_json)
            try:
                # Send json string to Arduino
                self.connection_dialog.master_serial.serialWrite('D')
                self.connection_dialog.master_serial.serialWrite(scan_function_json + '#')
            except:
                # If serial write fails, signal error
                self.announcer.appendPlainText("No serial port found")

    def uploadScanFunction(self):
        try:
            self.connection_dialog.master_serial.serialWrite('U')
        except:
            self.announcer.appendPlainText("No serial port found")

    def runScanFunction(self):
        try:
            self.connection_dialog.master_serial.serialWrite('R')
        except:
            self.announcer.appendPlainText("No serial port found")

    def stopScanFunction(self):
        try:
            self.connection_dialog.master_serial.serialWrite('S')
        except:
            self.announcer.appendPlainText("No serial port found")
