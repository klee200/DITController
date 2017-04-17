import sys
import pdb
import serial
from PyQt5.QtWidgets import *
from pyqtgraph import *
from ui.ScanFunction import ScanFunction
from ui.Communication import *
from ui.DialogWindows import ConnectionDialog

class MainWindow(QMainWindow):
    def __init__(self):
        # Call parent constructor
        super(MainWindow, self).__init__()
        # Create splitter for left and right halves and make it the central widget
        self.main_splitter = QSplitter()
        self.main_splitter.setContentsMargins(10,10,10,10)
        self.setCentralWidget(self.main_splitter)

        # Left half of main layout has two vertically stacked sections
        self.left_splitter = QSplitter()
        self.left_splitter.setOrientation(QtCore.Qt.Vertical)
        # Add left half to main splitter
        self.main_splitter.addWidget(self.left_splitter)

        # Right half of main layout has two vertically stacked sections
        self.right_layout = QVBoxLayout()
        self.right_layout.setContentsMargins(0,0,0,0)
        self.right_half = QWidget()
        self.right_half.setLayout(self.right_layout)
        # Add right half to main splitter
        self.main_splitter.addWidget(self.right_half)

        # Top left displays scan sections
        self.scan_area = QScrollArea()
        self.scan_layout = QHBoxLayout()
        self.scan_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.scan_widget = QWidget()
        self.scan_widget.setLayout(self.scan_layout)
        self.scan_area.setWidget(self.scan_widget)
        self.scan_area.setWidgetResizable(True)
        # Add scan area to left splitter
        self.left_splitter.addWidget(self.scan_area)

        # Bottom left displays plot of scan sections
        self.plot = PlotWidget()
        self.plot.setLabel('left', text='Frequency', units='Hz')
        self.plot.setLabel('bottom', text='Time', units='ms')
        # Add plot to left splitter
        self.left_splitter.addWidget(self.plot)

        # Top right displays buttons in grid layout
        self.button_layout = QGridLayout()
        # Add button layout to right half
        self.right_layout.addLayout(self.button_layout)
        # Create buttons at locations (row, column) in grid
        # Add scan segment button
        self.add_button = QPushButton("Add Segment")
        self.button_layout.addWidget(self.add_button, 1, 1)
        # Add scan segment button function
        self.add_button.clicked.connect(self.addScanSegment)
        # Remove scan segment button
        self.remove_button = QPushButton("Remove Segment")
        self.button_layout.addWidget(self.remove_button, 1, 2)
        # Remove scan segment button function
        self.remove_button.clicked.connect(self.removeScanSegment)
        # Download button
        self.download_button = QPushButton("Download Scan")
        self.button_layout.addWidget(self.download_button, 2, 1)
        # Download button function
        self.download_button.clicked.connect(self.downloadScanFunction)
        # Upload button
        self.upload_button = QPushButton("Upload Scan")
        self.button_layout.addWidget(self.upload_button, 2, 2)
        # Upload button function
        self.upload_button.clicked.connect(self.uploadScanFunction)
        # Run button
        self.run_button = QPushButton("Run Scan")
        self.button_layout.addWidget(self.run_button, 3, 1)
        # Run button function
        self.run_button.clicked.connect(self.runScanFunction)
        # Stop button
        self.stop_button = QPushButton("Stop Scan")
        self.button_layout.addWidget(self.stop_button, 3, 2)
        # Stop button function
        self.stop_button.clicked.connect(self.stopScanFunction)

        # Bottom right displays announcer
        self.announcer = QPlainTextEdit()
        self.announcer.setReadOnly(True)
        # Add announcer to right half
        self.right_layout.addWidget(self.announcer)

        # Create menu
        self.menuBar()
        self.menuBar().addMenu("File")
        self.settings_menu = self.menuBar().addMenu("Settings")
        self.connection = self.settings_menu.addAction("Connect")
        # Create connection dialog box
        self.connection_dialog = ConnectionDialog(self.announcer)
        # Show dialog box when button is clicked
        self.connection.triggered.connect(self.connection_dialog.show)

        # Create scan function object
        self.scan_function = ScanFunction()

    def addScanSegment(self):
        # Tell Scan Function object to add a new Segment object
        self.scan_function.addSegment()
        # Create new widget in Main Window for last segment in scan function
        self.scan_layout.addWidget(self.scan_function.scan_list[-1])
        # Announce segment creation
        self.announcer.appendPlainText("New segment added")

    def removeScanSegment(self):
        try:
            # Remove segment widget from layout
            self.scan_function.scan_list[-1].hide()
            self.scan_layout.removeWidget(self.scan_function.scan_list[-1])
            # Tell Scan function object to remove segment object
            self.scan_function.removeSegment()
            # Announce segment removal
            self.announcer.appendPlainText("Segment removed")
        except:
            # If no segment, announce error
            self.announcer.appendPlainText("No segment to remove")

    def downloadScanFunction(self):
        # Convert list into json string
        scan_function_json = convertToJson(self.scan_function.scan_list)
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

def main():
    app = QApplication(sys.argv)
    controller_interface = MainWindow()
    controller_interface.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
