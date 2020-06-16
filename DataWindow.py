from PyQt5.QtWidgets import QMainWindow, QWidget, QGridLayout, QPushButton, QLabel, QLineEdit, QFileDialog
from PyQt5.QtCore import pyqtSignal
import pyqtgraph as pg
# import pdb

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class DataWindow(QMainWindow):
    def __init__(self):
        super(DataWindow, self).__init__()
        
        self.setWindowTitle("Data Collector and Viewer")
        
        self.isClosable = False
        
        self.dataToolWidget = DataToolWidget()
        self.dataPlot = DataPlot()
        self.displayToolWidget = DisplayToolWidget()
        self.displayPlot = DisplayPlot()
        self.integralToolWidget = IntegralToolWidget()
        self.integralPlot = IntegralPlot()
        
        self.build_window()
        
        self.signal_handler()
        
        self.show()
        self.setGeometry(0,0,1000,800)
    
    def build_window(self):
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QGridLayout())
        
        self.centralWidget().layout().addWidget(self.dataToolWidget, 0, 0)
        self.centralWidget().layout().addWidget(self.dataPlot, 1, 0)
        self.centralWidget().layout().addWidget(self.displayToolWidget, 2, 0)
        self.centralWidget().layout().addWidget(self.displayPlot, 3, 0)
        self.centralWidget().layout().addWidget(self.integralToolWidget, 4, 0)
        self.centralWidget().layout().addWidget(self.integralPlot, 5, 0)
        
    def signal_handler(self):
        self.dataToolWidget.saveBtn.clicked.connect(self.dataPlot.save_data)
        self.dataToolWidget.averagesBox.textChanged.connect(self.dataPlot.set_averages)
        self.dataPlot.countSignal.connect(self.dataToolWidget.countBox.setText)
        self.dataPlot.integralSignal.connect(self.integralPlot.update)
        self.dataToolWidget.calibrateBtn.clicked.connect(lambda: self.dataPlot.calibrate(self.dataToolWidget.constBox.text(), self.dataToolWidget.startFreqBox.text(), self.dataToolWidget.endFreqBox.text()))
        
        self.displayToolWidget.openBtn.clicked.connect(self.displayPlot.open_data)
        self.displayToolWidget.saveBtn.clicked.connect(self.displayPlot.save_data)
        self.displayToolWidget.calibrateBtn.clicked.connect(lambda: self.displayPlot.calibrate(self.displayToolWidget.constBox.text(), self.displayToolWidget.startFreqBox.text(), self.displayToolWidget.endFreqBox.text()))
        
        self.integralToolWidget.clearBtn.clicked.connect(self.integralPlot.clr)
        
    def closeEvent(self, event):
        if self.isClosable:
            event.accept()
        else:
            event.ignore()
        # self.update()
        
class DataToolWidget(QWidget):
    def __init__(self):
        super(DataToolWidget, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QGridLayout())
        
        self.saveBtn = QPushButton("Save")
        self.layout().addWidget(self.saveBtn, 0, 0)
        
        self.layout().addWidget(QLabel("Averages"), 0, 1)
        self.countBox = QLineEdit("0")
        self.countBox.setEnabled(False)
        self.layout().addWidget(self.countBox, 0, 2)
        self.averagesBox = QLineEdit("1")
        self.layout().addWidget(self.averagesBox, 0, 3)
        
        self.layout().addWidget(QLabel("Frequencies"), 0, 4)
        self.startFreqBox = QLineEdit()
        self.layout().addWidget(self.startFreqBox, 0, 5)
        self.endFreqBox = QLineEdit()
        self.layout().addWidget(self.endFreqBox, 0, 6)
        
        self.layout().addWidget(QLabel("Constant"), 0, 7)
        self.constBox = QLineEdit()
        self.layout().addWidget(self.constBox, 0, 8)
        self.calibrateBtn = QPushButton("Calibrate")
        self.layout().addWidget(self.calibrateBtn, 0, 9)
                    
class DisplayToolWidget(QWidget):
    def __init__(self):
        super(DisplayToolWidget, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QGridLayout())
        
        self.openBtn = QPushButton("Open")
        self.layout().addWidget(self.openBtn, 0, 0)
        self.saveBtn = QPushButton("Save")
        self.layout().addWidget(self.saveBtn, 0, 1)
        
        self.layout().addWidget(QLabel("Frequencies"), 0, 2)
        self.startFreqBox = QLineEdit()
        self.layout().addWidget(self.startFreqBox, 0, 3)
        self.endFreqBox = QLineEdit()
        self.layout().addWidget(self.endFreqBox, 0, 4)
        
        self.layout().addWidget(QLabel("Constant"), 0, 5)
        self.constBox = QLineEdit()
        self.layout().addWidget(self.constBox, 0, 6)
        self.calibrateBtn = QPushButton("Calibrate")
        self.layout().addWidget(self.calibrateBtn, 0, 7)
        
class IntegralToolWidget(QWidget):
    def __init__(self):
        super(IntegralToolWidget, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QGridLayout())
        
        self.clearBtn = QPushButton("Clear")
        self.layout().addWidget(self.clearBtn, 0, 0)
       
class Plot(pg.PlotWidget):
    def __init__(self):
        super(Plot, self).__init__()
        
        self.x = []
        self.y = []
        
        self.build_widget()
        
    def build_widget(self):
        self.getPlotItem().getAxis('left').setStyle(tickLength=5)
        self.getPlotItem().getAxis('bottom').setStyle(tickLength=5)
        self.setLabel('bottom', text='m/z')
        self.setLabel('left', text='Intensity')
        self.setDownsampling(auto=True, mode='mean')
        self.setClipToView(True)
            
    def save_data(self):
        try:
            fileName = QFileDialog.getSaveFileName(filter='Text Files (*.txt)')[0]
            file = open(fileName, 'w')
            if len(self.x) < len(self.y):
                self.x = range(len(self.y))
            for i in range(len(self.y)):
                file.write(str(self.x[i]))
                file.write("\t")
                file.write(str(self.y[i]))
                file.write("\n")
            file.close()
        except FileNotFoundError:
            None    
            
    def calibrate(self, constant, startFreq, endFreq):
        try:
            startMz = float(constant) / float(startFreq)**2
            endMz = float(constant) / float(endFreq)**2
            stepMz = (endMz - startMz) / len(self.y)
            self.x = [startMz + i * stepMz for i in range(len(self.y))]
        except (ValueError, ZeroDivisionError) as error:
            self.x = range(len(self.y))
        
        if len(self.x) > 0:
            self.plot(self.x, self.y, clear=True)

class DataPlot(Plot):
    countSignal = pyqtSignal(object)
    integralSignal = pyqtSignal(object)
    def __init__(self):
        super(DataPlot, self).__init__()
        
        self.dataSample = 4
        self.numAverages = 1
        self.data = []
        
        self.build_widget()

    def update(self, data_string):
        self.data.append([data_string[j * 2] + data_string[j * 2 + 1] * 256 for j in range(0, int(len(data_string) / 2), self.dataSample)])
        if abs(len(self.data[-1]) - len(self.y)) > 10 and self.numAverages > 1:
            self.data.pop(-1)
        else:
            if len(self.data) > self.numAverages:
                self.data = self.data[-self.numAverages:]
            self.y = [sum(d) / len(self.data) for d in zip(*self.data)]
            if len(self.y) > 0:
                if len(self.x) != len(self.y):
                    self.x = range(len(self.y))
                self.plot(self.x, self.y, clear=True)
            self.countSignal.emit(str(len(self.data)))
            self.integralSignal.emit(sum(self.data[-1]))
        
    def set_averages(self, value):
        try:
            self.numAverages = int(value)
        except ValueError:
            self.numAverages = 1
    
    def set_sample(self, value):
        try:
            self.dataSample = int(value)
        except ValueError:
            self.dataSample = 4
               
class DisplayPlot(Plot):
    def __init__(self):
        super(DisplayPlot, self).__init__()
        
        self.build_widget()
        
    def open_data(self):            
        fileName = QFileDialog.getOpenFileName(filter='Text Files (*.txt)')[0]
        try:
            file = open(fileName, 'r')
            
            self.x = []
            self.y = []
            
            for line in file.readlines():
                pair = line.strip('\n').split('\t')
                self.x.append(float(pair[0]))
                self.y.append(float(pair[1]))
            file.close()
            
            self.plot(self.x, self.y, clear=True)
        except:
            None

class IntegralPlot(Plot):
    def __init__(self):
        super(IntegralPlot, self).__init__()
        
        self.data = []
        
        self.build_widget()
        
    def build_widget(self):
        super(IntegralPlot, self).build_widget()
        self.setLabel('bottom', text='Time')
        
    def update(self, point):
        self.data.append(point)
        self.x = range(len(self.data))
        self.y = self.data
        if len(self.y) > 1:
            self.plot(self.x, self.y, clear=True)
            
    def clr(self):
        self.data = []