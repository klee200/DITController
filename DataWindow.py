from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import pyqtgraph as pg
import pdb

pg.setConfigOption('background', 'w')
pg.setConfigOption('foreground', 'k')

class DataWindow(QMainWindow):
    def __init__(self, dataPlotTrigger):
        super(DataWindow, self).__init__()
        
        self.toolWidget = ToolWidget()
        self.dataPlot = DataPlot(dataPlotTrigger)
        self.displayDataPlot = DisplayDataPlot()
        
        self.build_window()
        
        self.signal_handler()
        
        self.show()
        self.setGeometry(0,0,1000,500)
    
    def build_window(self):
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(QGridLayout())
        
        self.centralWidget().layout().addWidget(self.toolWidget, 0, 0)
        self.centralWidget().layout().addWidget(self.dataPlot, 1, 0)
        self.centralWidget().layout().addWidget(self.displayDataPlot, 2, 0)
        
    def signal_handler(self):
        self.toolWidget.averagesBox.textChanged.connect(self.dataPlot.update_averages)
        self.dataPlot.averageSignal.connect(self.toolWidget.countBox.setText)
        self.toolWidget.saveBtn.clicked.connect(self.dataPlot.save_data)
        self.toolWidget.openBtn.clicked.connect(self.displayDataPlot.open_data)
        
    def closeEvent(self, event):
        event.ignore()
        
class ToolWidget(QWidget):
    def __init__(self):
        super(ToolWidget, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLayout(QHBoxLayout())
        self.saveBtn = QPushButton("Save")
        self.layout().addWidget(self.saveBtn)
        self.openBtn = QPushButton("Open")
        self.layout().addWidget(self.openBtn)
        self.layout().addWidget(QLabel("Averages"))
        self.countBox = QLineEdit("0")
        self.countBox.setEnabled(False)
        self.layout().addWidget(self.countBox)
        self.averagesBox = QLineEdit("1")
        self.layout().addWidget(self.averagesBox)
                    
class DataPlot(pg.PlotWidget):
    averageSignal = pyqtSignal(object)
    def __init__(self, dataPlotTrigger):
        super(DataPlot, self).__init__()
        
        self.dataPlotTrigger = dataPlotTrigger
        self.numAverages = 1
        self.data = []
        self.plotData = []
        
        self.build_widget()
        
    def build_widget(self):
        self.setLabel('bottom', text='Data point')
        self.setLabel('left', text='Intensity')
        self.setDownsampling(auto=True, mode='mean')
        self.setClipToView(True)

    def update(self, data_string):
        self.dataPlotTrigger = False
        self.data.append([data_string[j * 2] + data_string[j * 2 + 1] * 256 for j in range(int(len(data_string) / 2))])
        if len(self.data) > self.numAverages:
            self.data = self.data[-self.numAverages:]
            self.plotData = [sum(i) / len(self.data) for i in zip(*self.data)]
        else:
            self.plotData = [(self.plotData[i] * (len(self.data) - 1) + self.data[-1][i]) / len(self.data) for i in range(len(self.plotData)) if len(self.data[-1]) >= len(self.plotData)]
        print(len(self.data))
        self.averageSignal.emit(str(len(self.data)))
        print(len(self.plotData))
        if len(self.plotData) > 0:
            self.plot(range(len(self.plotData)), self.plotData, clear=True)
        self.dataPlotTrigger = True
        
    def update_averages(self, value):
        try:
            self.numAverages = int(value)
        except ValueError:
            self.numAverages = 1
            
    def save_data(self):
        fileName = QFileDialog.getSaveFileName(filter='Text Files (*.txt)')[0]
        file = open(fileName, 'w')
        for i in range(len(self.plotData)):
            file.write(str(i + 1))
            file.write("\t")
            file.write(str(self.plotData[i]))
            file.write("\n")
        file.close()
        
class DisplayDataPlot(pg.PlotWidget):
    def __init__(self):
        super(DisplayDataPlot, self).__init__()
        
        self.build_widget()
        
    def build_widget(self):
        self.setLabel('bottom', text='Data point')
        self.setLabel('left', text='Intensity')
        self.setDownsampling(auto=True, mode='mean')
        self.setClipToView(True)
        
    def open_data(self):            
        fileName = QFileDialog.getOpenFileName(filter='Text Files (*.txt)')[0]
        try:
            file = open(fileName, 'r')
            
            x = []
            y = []
            
            for line in file.readlines():
                pair = line.strip('\n').split('\t')
                x.append(float(pair[0]))
                y.append(float(pair[1]))
            file.close()
            
            self.plot(x, y, clear=True)
        except:
            None