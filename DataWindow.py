from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import pdb

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class DataWindow(QMainWindow):
    def __init__(self, dataPlotTrigger):
        super(DataWindow, self).__init__()
        
        self.dataToolWidget = DataToolWidget()
        self.dataPlot = DataPlot(dataPlotTrigger)
        self.displayToolWidget = DisplayToolWidget()
        self.displayPlot = DisplayPlot()
        
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
        
    def signal_handler(self):
        self.dataToolWidget.saveBtn.clicked.connect(self.dataPlot.save_data)
        self.dataToolWidget.averagesBox.textChanged.connect(self.dataPlot.set_averages)
        self.dataPlot.updated.connect(self.dataToolWidget.countBox.setText)
        self.dataToolWidget.calibrateBtn.clicked.connect(lambda: self.dataPlot.calibrate(self.dataToolWidget.constBox.text(), self.dataToolWidget.startFreqBox.text(), self.dataToolWidget.endFreqBox.text()))
        
        self.displayToolWidget.openBtn.clicked.connect(self.displayPlot.open_data)
        self.displayToolWidget.saveBtn.clicked.connect(self.displayPlot.save_data)
        self.displayToolWidget.calibrateBtn.clicked.connect(lambda: self.displayPlot.calibrate(self.displayToolWidget.constBox.text(), self.displayToolWidget.startFreqBox.text(), self.displayToolWidget.endFreqBox.text()))
        
    def closeEvent(self, event):
        event.ignore()
        
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
        
        self.layout().addWidget(QLabel("Constant"), 1, 4)
        self.constBox = QLineEdit()
        self.layout().addWidget(self.constBox, 1, 5)
        self.calibrateBtn = QPushButton("Calibrate")
        self.layout().addWidget(self.calibrateBtn, 1, 6)
                    
class DisplayToolWidget(QWidget):
    def __init__(self):
        super(DisplayToolWidget, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QGridLayout())
        self.saveBtn = QPushButton("Save")
        self.layout().addWidget(self.saveBtn, 0, 0)
        self.openBtn = QPushButton("Open")
        self.layout().addWidget(self.openBtn, 1, 0)
        
        self.layout().addWidget(QLabel("Averages"), 0, 1)
        self.countBox = QLineEdit("0")
        self.countBox.setEnabled(False)
        self.layout().addWidget(self.countBox, 0, 2)
        self.averagesBox = QLineEdit("1")
        self.layout().addWidget(self.averagesBox, 1, 2)
        
        self.layout().addWidget(QLabel("Frequencies"), 0, 4)
        self.startFreqBox = QLineEdit()
        self.layout().addWidget(self.startFreqBox, 0, 5)
        self.endFreqBox = QLineEdit()
        self.layout().addWidget(self.endFreqBox, 0, 6)
        
        self.layout().addWidget(QLabel("Constant"), 1, 4)
        self.constBox = QLineEdit()
        self.layout().addWidget(self.constBox, 1, 5)
        self.calibrateBtn = QPushButton("Calibrate")
        self.layout().addWidget(self.calibrateBtn, 1, 6)
       
class Plot(pg.PlotWidget):
    def __init__(self):
        super(Plot, self).__init__()
        
        self.x = [0, 1000]
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
            for i in range(len(self.x)):
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
        except ValueError:
            self.x = range(len(self.y))
        print(len(self.x))
        
        if len(self.x) > 0:
            self.plot(self.x, self.y, clear=True)

class DataPlot(Plot):
    updated = pyqtSignal(object)
    def __init__(self, dataPlotTrigger):
        super(DataPlot, self).__init__()
        
        self.dataPlotTrigger = dataPlotTrigger
        self.numAverages = 1
        self.data = []
        
        self.build_widget()

    def update(self, data_string):
        self.dataPlotTrigger = False
        self.data.append([data_string[j * 2] + data_string[j * 2 + 1] * 256 for j in range(int(len(data_string) / 2))])
        if len(self.data) > self.numAverages:
            self.data = self.data[-self.numAverages:]
            self.y = [sum(i) / len(self.data) for i in zip(*self.data)]
        else:
            self.y = [(self.y[i] * (len(self.data) - 1) + self.data[-1][i]) / len(self.data) for i in range(len(self.y)) if len(self.data[-1]) >= len(self.y)]
        print(len(self.y))
        if len(self.y) > 0:
            if len(self.x) > len(self.y):
                self.plot(self.x[0:len(self.y)], self.y, clear=True)
            else:
                self.plot(range(len(self.y)), self.y, clear=True)
        self.updated.emit(str(len(self.data)))
        self.dataPlotTrigger = True
        
    def set_averages(self, value):
        try:
            self.numAverages = int(value)
        except ValueError:
            self.numAverages = 1
            
    # def calibrate(self, constant, startFreq, endFreq):
        # try:
            # self.axisLimits[0] = float(constant) / float(startFreq)**2
            # self.axisLimits[1] = float(constant) / float(endFreq)**2
        # except ValueError:
            # self.axisLimits = [0, 1000]
        # print(self.axisLimits)
               
class DisplayPlot(Plot):
    def __init__(self):
        super(DisplayPlot, self).__init__()
        
        self.x = [0, 1000]
        self.y = []
        
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
        except FileNotFoundError:
            None