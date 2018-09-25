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

class ScanWidget(QSplitter):
    def __init__(self, textWidget):
        super(ScanWidget, self).__init__(Qt.Vertical)
        
        self.textWidget = textWidget
        self.scanFunction = ScanFunction()
        
        self.scanArea = ScanArea(self.scanFunction)
        
        self.build_widget()
        
    def build_widget(self):
        self.addWidget(self.scanArea)
        
    def save_check(self):
        msgBox = QMessageBox()
        msgBox.setText("Do you want to save the current scan?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        return msgBox.exec()
        
    def save_scan(self):
        try:
            fileName = QFileDialog.getSaveFileName(filter='Scan Files (*.scan);;Text Files (*.txt)')[0]
            file = open(fileName, 'w')
            file.write(json.dumps(self.scanFunction, sort_keys=False, indent=4))
            file.close()
            
            scanPic = self.scanArea.widget().grab()
            scanPicFileName = fileName.replace('.scan', '.jpg')
            scanPic.save(scanPicFileName, 'jpg')
        except FileNotFoundError:
            self.textWidget.appendPlainText("File save failed")
        
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
                
                file.close()
            except FileNotFoundError:
                self.textWidget.appendPlainText("File open failed")
        
class ScanArea(QScrollArea):
    def __init__(self, scanFunction):
        super(ScanArea, self).__init__()
        
        self.headerLabels = ["Name", "Active", "Record", "Duration"]
        self.headerTypes = [str, Bool, Bool, PosFloat]
        self.OUTPUTS = 3
        self.outputLabels = ["Start", "End", "Duty Cycle", "Tickle", "Amplitude", "Phase"]
        self.outputTypes = [FreqFloat, FreqFloat, DCFloat, DivChoice, AmpFloat, PhaseChoice]
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
        
    def flags(self, index):
        return Qt.ItemIsEditable | QAbstractTableModel.flags(self, index)
        
class HeaderModel(ParameterModel):
    def __init__(self, scanFunction, labels, types):
        super(HeaderModel, self).__init__(scanFunction, labels, types)
                                
    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self.scanFunction[index.column()][self.labels[index.row()]])
        if role == Qt.BackgroundRole:
            if self.scanFunction[index.column()][self.labels[index.row()]] == "False":
                return QBrush(QColor('red'))
            elif self.scanFunction[index.column()][self.labels[index.row()]] == "True":
                return QBrush(QColor('green'))
            else:
                return QBrush(QColor('white'))
                    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
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
        if role == Qt.ToolTipRole:
            if self.labels[index.row()] == "Tickle":
                return "Div / [value here] or Output 3"
            if self.labels[index.row()] == "Phase":
                return "0 or 180 (degrees)"
        
    def setData(self, index, value, role):
        if role == Qt.EditRole:
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
        if role == Qt.BackgroundRole:
            if self.scanFunction[index.column()][self.name][index.row()] == "False":
                return QBrush(QColor('red'))
            elif self.scanFunction[index.column()][self.name][index.row()] == "True":
                return QBrush(QColor('green'))
            else:
                return QBrush(QColor('white'))
        
    def setData(self, index, value, role):
        if role == Qt.EditRole:
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
        
class PhaseChoice(int):
    def __new__(cls, value):
        try:
            v = int(value)
            if v == 0:
                s = v
            else:
                s = 180
        except ValueError:
            s = 0
        return s