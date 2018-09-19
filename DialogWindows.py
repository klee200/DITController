from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from ScanFunction import *
from SerialPorts import *

class ConnectionWindow(QDialog):
    def __init__(self, textWidget):
        super(ConnectionWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.textWidget = textWidget
        
        self.controlPort = ControlPort()
        self.dataPort = DataPort(self.controlPort)
        
        self.build_window()

    def build_window(self):
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Control"), 0, 0)
        self.controlBox = QLineEdit("COM7")
        self.layout().addWidget(self.controlBox, 0, 1)
        
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.layout().addWidget(self.line, 2, 0, 1, 2)
        
        self.layout().addWidget(QLabel("Data"), 3, 0)
        self.dataBox = QLineEdit("COM6")
        self.layout().addWidget(self.dataBox, 3, 1)
        
        self.controlConnectBtn = QPushButton('Connect Controller')
        self.layout().addWidget(self.controlConnectBtn, 1, 0)
        self.controlDisconnectBtn = QPushButton('Disconnect Controller')
        self.layout().addWidget(self.controlDisconnectBtn, 1, 1)
        self.dataConnectBtn = QPushButton('Connect Data')
        self.layout().addWidget(self.dataConnectBtn, 4, 0)
        self.dataDisconnectBtn = QPushButton('Disconnect Data')
        self.layout().addWidget(self.dataDisconnectBtn, 4, 1)

    def connect_control(self):
        try:
            # self.controlPort = ControlPort(self.controlBox.text())
            self.controlPort.port = self.controlBox.text()
            self.controlPort.open()
            self.textWidget.appendPlainText("Controller connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")

    def disconnect_control(self):
        try:
            self.controlPort.close()
            # del(self.controlPort)
            self.textWidget.appendPlainText("Controller disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")
        
    def connect_data(self):
        try:
            # self.dataPort = DataPort(self.dataBox.text(), self.controlPort)
            self.dataPort.port = self.dataBox.text()
            self.dataPort.open()
            self.dataPort.dataThread.start()
            # self.mainWindow.averages_box.textChanged.connect(self.dataPort.update)
            # self.dataPort.dataThread.updateSignal.connect(self.mainWindow.dataPlot.updatePlot)
            self.textWidget.appendPlainText("Data serial connected")
        except SerialException:
            self.textWidget.appendPlainText("No serial port found")
        
    def disconnect_data(self):
        try:
            self.dataPort.close()
            # del(self.dataPort)
            self.textWidget.appendPlainText("Data serial disconnected")
        except SerialException:
            self.textWidget.appendPlainText("No connection found")


class AddRemoveSegmentWindow(QDialog):
    def __init__(self):
        super(AddRemoveSegmentWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.build_window()
        
    def build_window(self):
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Insert new segment at position:"), 1, 0)
        self.addPositionBox = QLineEdit("1")
        self.layout().addWidget(self.addPositionBox, 1, 1)
        self.layout().addWidget(QLabel("Remove segment from position:"), 3, 0)
        self.removePositionBox = QLineEdit("1")
        self.layout().addWidget(self.removePositionBox, 3, 1)
        
        self.addSegBtn = QPushButton("Insert segment")
        self.layout().addWidget(self.addSegBtn, 2, 0, 1, 2)
        self.removeSegBtn = QPushButton("Remove segment")
        self.layout().addWidget(self.removeSegBtn, 4, 0, 1, 2)


class CopySegmentWindow(QDialog):
    def __init__(self, mainWindow):
        super(CopySegmentWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.mainWindow = mainWindow
        self.build_window()
        
    def build_window(self):
        self.setLayout(QGridLayout())
        
        self.layout().addWidget(QLabel("Copy segment:"), 0, 0)
        self.copyBox = QLineEdit()
        self.layout().addWidget(self.copyBox, 0, 1)
        self.layout().addWidget(QLabel("to:"), 1, 0)
        self.pasteBox = QLineEdit()
        self.layout().addWidget(self.pasteBox, 1, 1)
        
        self.copyBtn = QPushButton("Do it")
        self.layout().addWidget(self.copyBtn)

class CalculatorWindow(QDialog):
    def __init__(self, mainWindow):
        super(CalculatorWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.mainWindow = mainWindow
        # Make layout
        self.setLayout(QGridLayout())
        # Constants
        self.electron = 1.602e-19
        self.amu = 1.66e-27
        # Make labels and boxes
        self.layout().addWidget(QLabel("r\u2080 (cm)"), 0, 0)
        self.r_box = QLineEdit("0.707")
        self.layout().addWidget(self.r_box, 0, 1)
        self.layout().addWidget(QLabel("z\u2080 (cm)"), 1, 0)
        self.z_box = QLineEdit("0.774")
        self.layout().addWidget(self.z_box, 1, 1)
        self.layout().addWidget(QLabel("High V (V)"), 0, 2)
        self.high_v_box = QLineEdit("200")
        self.layout().addWidget(self.high_v_box, 0, 3)
        self.layout().addWidget(QLabel("Low V (V)"), 1, 2)
        self.low_v_box = QLineEdit("-200")
        self.layout().addWidget(self.low_v_box, 1, 3)
        self.layout().addWidget(QLabel("Duty Cycle (%)"), 2, 2)
        self.d_box = QLineEdit("50")
        self.layout().addWidget(self.d_box, 2, 3)
        # self.layout().addWidget(QLabel("a"), 0, 4)
        # self.a_z_box = QLineEdit()
        # self.a_z_box.setEnabled(False)  # Make a not editable
        # self.layout().addWidget(self.a_z_box, 0, 5)
        # self.layout().addWidget(QLabel("q"), 1, 4)
        # self.q_z_box = QLineEdit(self.mainWindow.default_q_z)
        # self.layout().addWidget(self.q_z_box, 1, 5)
        self.layout().addWidget(QLabel("Beta r"), 4, 0)
        self.beta_r_box = QLineEdit()
        self.layout().addWidget(self.beta_r_box, 4, 1)
        self.beta_r_box.setEnabled(False)  # Make beta not editable
        self.layout().addWidget(QLabel("Beta z"), 4, 2)
        self.beta_z_box = QLineEdit()
        self.layout().addWidget(self.beta_z_box, 4, 3)
        self.beta_z_box.setEnabled(False)  # Make beta not editable
        # Make horizontal line
        self.line = QFrame()
        self.line.setFrameShape(QFrame.HLine)
        self.layout().addWidget(self.line, 3, 0, 1, 6)
        # Make m/z and frequency boxes
        self.layout().addWidget(QLabel("Drive frequency (Hz)"), 0, 4)
        self.frequency_box = QLineEdit("200000")
        self.layout().addWidget(self.frequency_box, 0, 5)
        self.layout().addWidget(QLabel("m/z"), 1, 4)
        self.mass_box = QLineEdit("2000")
        self.layout().addWidget(self.mass_box, 1, 5)
        self.layout().addWidget(QLabel("Ion frequency (Hz)"), 4, 4)
        self.ion_freq_box = QLineEdit()
        self.layout().addWidget(self.ion_freq_box, 4, 5)
        self.ion_freq_box.setEnabled(False)  # Make ion frequency not editable
        # Find boundary button and functionality
        self.beta_select = QComboBox()
        self.layout().addWidget(self.beta_select, 2, 4)
        self.beta_select.addItem("1")
        self.beta_select.addItem("0.5")
        self.beta_select.addItem("0.25")
        self.beta_select.addItem("0.125")
        self.find_boundary_button = QPushButton("Find boundary")
        self.layout().addWidget(self.find_boundary_button, 2, 5)
        self.find_boundary_button.clicked.connect(self.findBoundary)
        # Make conversion constant box
        # self.layout().addWidget(QLabel("Drive constant"), 4, 4)
        # self.drive_const_box = QLineEdit()
        # self.layout().addWidget(self.drive_const_box, 4, 5)
        # self.layout().addWidget(QLabel("Tickle constant"), 5, 4)
        # self.tickle_const_box = QLineEdit()
        # self.layout().addWidget(self.tickle_const_box, 5, 5)
        # self.button = QPushButton("Copy constants")
        # self.layout().addWidget(self.button, 6, 5)
        # self.button.clicked.connect(self.copyConstants)
        # self.save_default_button = QPushButton("Save as default")
        # self.layout().addWidget(self.save_default_button, 6, 0)
        # self.save_default_button.clicked.connect(self.saveDefaults)
        # self.close_button = QPushButton("Close")
        # self.layout().addWidget(self.close_button, 6, 5)
        # self.close_button.clicked.connect(self.close)
        self.update()

        # Connect parameter boxes to conversion constant, a, and mass boxes
        # self.q_z_box.textEdited.connect(self.update)
        self.r_box.textChanged.connect(self.update)
        self.z_box.textChanged.connect(self.update)
        self.high_v_box.textChanged.connect(self.update)
        self.low_v_box.textChanged.connect(self.update)
        self.d_box.textChanged.connect(self.update)
        self.frequency_box.textChanged.connect(self.update)
        self.mass_box.textChanged.connect(self.update)
        # Connect frequency and m/z boxes
        # self.frequency_box.textEdited.connect(self.calculateMass)
        # self.frequency_box.textEdited.connect(self.calculateIonFreq)
        # self.mass_box.textEdited.connect(self.calculateFrequency)

    def update(self):
        # self.calculateAz()
        # self.calculateDriveConstant()
        # self.calculateMass()
        self.calculateBetaR()
        self.calculateBetaZ()
        self.calculateIonFreq()
        # self.calculateTickleConstant()

    # def calculateQz(self):
    #     # Calculate U and V
    #     try:
    #         U = float(self.d_box.text())/100 * float(self.high_v_box.text()) + (1 - float(self.d_box.text())/100) * float(self.low_v_box.text())
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (1 - float(self.d_box.text())/100) * float(self.d_box.text())/100
    #         q_z = str(-1 * float(self.a_z_box.text()) * V / 2 / U)
    #     except:
    #         q_z = None
    #
    #     self.q_z_box.setText(q_z)

    # def calculateAz(self):
    #     # Calculate U and V
    #     try:
    #         U = float(self.d_box.text()) / 100 * float(self.high_v_box.text()) + (1 - float(
    #             self.d_box.text()) / 100) * float(self.low_v_box.text())
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (
    #         1 - float(self.d_box.text()) / 100) * float(self.d_box.text()) / 100
    #         a_z = str(float(self.q_z_box.text()) * -2 * U / V)
    #     except:
    #         a_z = None
    #
    #     self.a_z_box.setText(a_z)

    # def calculateMass(self):
    #     # m/z = 8*e*V/(r^2+2z^2)/frequency^2/qz
    #     try:
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (
    #         1 - float(self.d_box.text()) / 100) * float(self.d_box.text()) / 100
    #         mass = str(8 * 1.602e-19 * V / (
    #         pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)) / pow(
    #             float(self.frequency_box.text()) * 2 * pi, 2) / float(self.q_z_box.text()) / 1.66e-27)
    #     except:
    #         mass = None
    #
    #     self.mass_box.setText(mass)

    # def calculateFrequency(self):
    #     try:
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (
    #         1 - float(self.d_box.text()) / 100) * float(self.d_box.text()) / 100
    #         frequency = str(sqrt(8 * 1.602e-19 * V / (
    #         pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)) / float(
    #             self.mass_box.text()) / float(self.q_z_box.text()) / 1.66e-27) / 2 / pi)
    #     except:
    #         frequency = None
    #
    #     self.frequency_box.setText(frequency)

    def calculateBetaR(self):
        try:
            delta_hi = float(self.d_box.text()) / 100 * pi
            delta_lo = (1 - float(self.d_box.text()) / 100) * pi

            f_r_hi = 2 * 4 * self.electron * float(self.high_v_box.text()) / (float(self.mass_box.text()) * self.amu * pow(float(self.frequency_box.text()) * 2 * pi, 2) * (pow(float(self.r_box.text()) / 100, 2) + 2* pow(float(self.z_box.text()) / 100, 2)))
            m_r_hi = [[0 for x in range(2)] for y in range(2)]
            if f_r_hi > 0:
                m_r_hi[0][0] = cos(sqrt(f_r_hi) * delta_hi)
                m_r_hi[0][1] = 1 / sqrt(f_r_hi) * sin(sqrt(f_r_hi) * delta_hi)
                m_r_hi[1][0] = -sqrt(f_r_hi) * sin(sqrt(f_r_hi) * delta_hi)
                m_r_hi[1][1] = cos(sqrt(f_r_hi) * delta_hi)
            else:
                m_r_hi[0][0] = cosh(sqrt(-f_r_hi) * delta_hi)
                m_r_hi[0][1] = 1 / sqrt(-f_r_hi) * sinh(sqrt(-f_r_hi) * delta_hi)
                m_r_hi[1][0] = sqrt(-f_r_hi) * sinh(sqrt(-f_r_hi) * delta_hi)
                m_r_hi[1][1] = cosh(sqrt(-f_r_hi) * delta_hi)

            f_r_lo = 2 * 4 * self.electron * float(self.low_v_box.text()) / (float(self.mass_box.text()) * self.amu * pow(float(self.frequency_box.text()) * 2 * pi, 2) * (pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)))
            m_r_lo = [[0 for x in range(2)] for y in range(2)]
            if f_r_lo > 0:
                m_r_lo[0][0] = cos(sqrt(f_r_lo) * delta_lo)
                m_r_lo[0][1] = 1 / sqrt(f_r_lo) * sin(sqrt(f_r_lo) * delta_lo)
                m_r_lo[1][0] = -sqrt(f_r_lo) * sin(sqrt(f_r_lo) * delta_lo)
                m_r_lo[1][1] = cos(sqrt(f_r_lo) * delta_lo)
            else:
                m_r_lo[0][0] = cosh(sqrt(-f_r_lo) * delta_lo)
                m_r_lo[0][1] = 1 / sqrt(-f_r_lo) * sinh(sqrt(-f_r_lo) * delta_lo)
                m_r_lo[1][0] = sqrt(-f_r_lo) * sinh(sqrt(-f_r_lo) * delta_lo)
                m_r_lo[1][1] = cosh(sqrt(-f_r_lo) * delta_lo)
            m_r = np.dot(m_r_hi, m_r_lo)
            beta_r = acos((m_r[0][0] + m_r[1][1]) / 2) / pi
        except:
            beta_r = inf
        self.beta_r_box.setText(str(beta_r))

    def calculateBetaZ(self):
        try:
            delta_hi = float(self.d_box.text()) / 100 * pi
            delta_lo = (1 - float(self.d_box.text()) / 100) * pi

            f_z_hi = -2 * 8 * self.electron * float(self.high_v_box.text()) / (float(self.mass_box.text()) * self.amu * pow(float(self.frequency_box.text()) * 2 * pi, 2) * (pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)))
            m_z_hi = [[0 for x in range(2)] for y in range(2)]
            if f_z_hi > 0:
                m_z_hi[0][0] = cos(sqrt(f_z_hi) * delta_hi)
                m_z_hi[0][1] = 1 / sqrt(f_z_hi) * sin(sqrt(f_z_hi) * delta_hi)
                m_z_hi[1][0] = -sqrt(f_z_hi) * sin(sqrt(f_z_hi) * delta_hi)
                m_z_hi[1][1] = cos(sqrt(f_z_hi) * delta_hi)
            else:
                m_z_hi[0][0] = cosh(sqrt(-f_z_hi) * delta_hi)
                m_z_hi[0][1] = 1 / sqrt(-f_z_hi) * sinh(sqrt(-f_z_hi) * delta_hi)
                m_z_hi[1][0] = sqrt(-f_z_hi) * sinh(sqrt(-f_z_hi) * delta_hi)
                m_z_hi[1][1] = cosh(sqrt(-f_z_hi) * delta_hi)

            f_z_lo = -2 * 8 * self.electron * float(self.low_v_box.text()) / (float(self.mass_box.text()) * self.amu * pow(float(self.frequency_box.text()) * 2 * pi, 2) * (pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)))
            m_z_lo = [[0 for x in range(2)] for y in range(2)]
            if f_z_lo > 0:
                m_z_lo[0][0] = cos(sqrt(f_z_lo) * delta_lo)
                m_z_lo[0][1] = 1 / sqrt(f_z_lo) * sin(sqrt(f_z_lo) * delta_lo)
                m_z_lo[1][0] = -sqrt(f_z_lo) * sin(sqrt(f_z_lo) * delta_lo)
                m_z_lo[1][1] = cos(sqrt(f_z_lo) * delta_lo)
            else:
                m_z_lo[0][0] = cosh(sqrt(-f_z_lo) * delta_lo)
                m_z_lo[0][1] = 1 / sqrt(-f_z_lo) * sinh(sqrt(-f_z_lo) * delta_lo)
                m_z_lo[1][0] = sqrt(-f_z_lo) * sinh(sqrt(-f_z_lo) * delta_lo)
                m_z_lo[1][1] = cosh(sqrt(-f_z_lo) * delta_lo)
            m_z = np.dot(m_z_hi, m_z_lo)
            beta_z = acos((m_z[0][0] + m_z[1][1]) / 2) / pi

            # K_hi = sqrt(float(self.q_z_box.text()) / (float(self.d_box.text()) / 100) - float(self.a_z_box.text()))
            # K_lo = sqrt(
            #     -1 * float(self.q_z_box.text()) / (float(self.d_box.text()) / 100 - 1) + float(self.a_z_box.text()))
            # phi_11 = cosh(K_hi * pi * float(self.d_box.text()) / 100) * cos(
            #     K_lo * pi * (1 - float(self.d_box.text()) / 100)) + K_hi / K_lo * sinh(
            #     K_hi * pi * float(self.d_box.text()) / 100) * sin(K_lo * pi * (1 - float(self.d_box.text()) / 100))
            # phi_22 = cosh(K_hi * pi * float(self.d_box.text()) / 100) * cos(
            #     K_lo * pi * (1 - float(self.d_box.text()) / 100)) - K_lo / K_hi * sinh(
            #     K_hi * pi * float(self.d_box.text()) / 100) * sin(K_lo * pi * (1 - float(self.d_box.text()) / 100))
            # beta = str(1 / pi * acos((phi_11 + phi_22) / 2))
        except:
            beta_z = inf
        self.beta_z_box.setText(str(beta_z))

    def calculateIonFreq(self):
        try:
            ion_freq = 1 / 2 * float(self.beta_z_box.text()) * float(self.frequency_box.text())
        except:
            ion_freq = None

        self.ion_freq_box.setText(str(ion_freq))

    # def calculateDriveConstant(self):
    #     try:
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (
    #         1 - float(self.d_box.text()) / 100) * float(self.d_box.text()) / 100
    #         constant = str((8 * 1.602e-19 * V / (
    #         pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)) / float(
    #             self.q_z_box.text()) / 1.66e-27) / pow(2 * pi, 2))
    #     except:
    #         constant = None
    #
    #     self.drive_const_box.setText(constant)

    # def calculateTickleConstant(self):
    #     try:
    #         V = 2 * (float(self.high_v_box.text()) - float(self.low_v_box.text())) * (
    #         1 - float(self.d_box.text()) / 100) * float(self.d_box.text()) / 100
    #         constant = str((8 * 1.602e-19 * V / (
    #         pow(float(self.r_box.text()) / 100, 2) + 2 * pow(float(self.z_box.text()) / 100, 2)) / float(
    #             self.q_z_box.text()) / 1.66e-27) / pow(2 * pi, 2) * pow(float(self.beta_box.text()), 2) / 4)
    #     except:
    #         constant = None
    #
    #     self.tickle_const_box.setText(constant)


    def findBoundary(self):
        for i in range(floor(log10(float(self.frequency_box.text()))), -1, -1):
            if float(self.beta_r_box.text()) == inf or float(self.beta_z_box.text()) == inf:
                None
            elif float(self.beta_z_box.text()) < float(self.beta_select.currentText()):
                while float(self.beta_z_box.text()) < float(self.beta_select.currentText()) and float(self.beta_r_box.text()) < inf and float(self.frequency_box.text()) > 0:
                    self.frequency_box.setText(str(float(self.frequency_box.text()) - pow(10, i)))
                self.frequency_box.setText(str(float(self.frequency_box.text()) + pow(10, i)))
            else:
                while float(self.beta_z_box.text()) > float(self.beta_select.currentText()) and float(self.beta_z_box.text()) < inf and float(self.beta_r_box.text()) < inf and float(self.frequency_box.text()) > 0:
                    self.frequency_box.setText(str(float(self.frequency_box.text()) + pow(10, i)))
                self.frequency_box.setText(str(float(self.frequency_box.text()) - pow(10, i)))

    # def copyConstants(self):
    #     self.mainWindow.conv_const_box.setText(self.drive_const_box.text())
    #     self.mainWindow.tickle_const_box.setText(self.tickle_const_box.text())
    #     self.close()

    # def saveDefaults(self):
    #     self.mainWindow.default_r = self.r_box.text()
    #     self.mainWindow.default_z = self.z_box.text()
    #     self.mainWindow.default_high_v = self.high_v_box.text()
    #     self.mainWindow.default_low_v = self.low_v_box.text()
    #     self.mainWindow.default_duty_cycle = self.d_box.text()
    #     self.mainWindow.default_q_z = self.q_z_box.text()

class PlotCalibrateWindow(QDialog):
    def __init__(self, mainWindow):
        super(PlotCalibrateWindow, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # Make layout
        self.setLayout(QHBoxLayout())
        # Add table to layout
        self.NUM_ROWS = 5
        self.NUM_COLS = 2
        self.peak_table = QTableWidget(self.NUM_ROWS, self.NUM_COLS)
        self.peak_table.setFixedHeight(HEIGHT * (self.NUM_ROWS + 1) + 2)
        self.peak_table.setFixedWidth(WIDTH * self.NUM_COLS + 2)
        self.peak_table.verticalHeader().setDefaultSectionSize(HEIGHT)
        self.peak_table.verticalHeader().hide()
        self.peak_table.horizontalHeader().setDefaultSectionSize(WIDTH)
        self.peak_table.setHorizontalHeaderLabels(['x', 'm/z'])
        self.layout().addWidget(self.peak_table)
        # Connect table to value update
        for i in range(self.NUM_ROWS):
            for j in range(self.NUM_COLS):
                self.peak_table.setItem(i, j, QTableWidgetItem())
        self.peak_table.itemChanged.connect(self.update)
        # Add parameter layout to layout
        self.parameter_layout = QGridLayout()
        self.layout().addLayout(self.parameter_layout)
        # Add slope parameter to layout
        self.parameter_layout.addWidget(QLabel("Slope"), 0, 0)
        self.slope_box = QLineEdit()
        self.slope_box.setEnabled(False)
        self.parameter_layout.addWidget(self.slope_box, 0, 1)
        # Add intercept parameter to layout
        self.parameter_layout.addWidget(QLabel("Intercept"), 1, 0)
        self.intercept_box = QLineEdit()
        self.intercept_box.setEnabled(False)
        self.parameter_layout.addWidget(self.intercept_box, 1, 1)
        # Add R^2 result to layout
        self.parameter_layout.addWidget(QLabel("R^2"), 2, 0)
        self.r_2_box = QLineEdit()
        self.r_2_box.setEnabled(False)
        self.parameter_layout.addWidget(self.r_2_box, 2, 1)
        
    def update(self):
        x = []
        y = []
        for i in range(self.NUM_ROWS):
            try:
                x.append(float(self.peak_table.item(i, 0).text()))
                y.append(float(self.peak_table.item(i, 1).text()))
            except:
                None
        self.calculateSlope(x, y)
        self.calculateIntercept(x, y)
        self.calculateR2(x, y)
        
    def calculateIntercept(self, x, y):
        try:
            intercept = (sum(y) * sum([i**2 for i in x]) - sum(x) * sum([i * j for i, j in zip(x, y)])) / (len(x) * sum([i**2 for i in x]) - sum(x)**2)
        except:
            intercept = None
        self.intercept_box.setText(str(intercept))
        
    def calculateSlope(self, x, y):
        try:
            slope = (len(x) * sum([i * j for i, j in zip(x, y)]) - sum(x) * sum(y)) / (len(x) * sum([i**2 for i in x]) - sum(x)**2)
        except:
            slope = None
        self.slope_box.setText(str(slope))
        
    def calculateR2(self, x, y):
        try:
            res = sum([(i - j)**2 for i, j in zip(y, [float(self.slope_box.text()) * i + float(self.intercept_box.text()) for i in x])])
            tot = sum([(i - sum(y)/len(y))**2 for i in y])
            r2 = 1 - res / tot
        except:
            r2 = None
        self.r_2_box.setText(str(r2))