import pdb
import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class SignalHandler(object):
    def __init__(self, mainWindow):
        mainWindow.saveAction.triggered.connect(mainWindow.scanWidget.save_scan)
        mainWindow.openAction.triggered.connect(mainWindow.scanWidget.open_scan)
        
        
        mainWindow.addRemoveAction.triggered.connect(mainWindow.addRemoveWindow.show)
        mainWindow.calcAction.triggered.connect(mainWindow.calcWindow.show)
        
        mainWindow.addRemoveWindow.addSegBtn.clicked.connect(lambda: mainWindow.scanWidget.scanArea.add_segment(int(mainWindow.addRemoveWindow.addPositionBox.text()) - 1))
        mainWindow.addRemoveWindow.removeSegBtn.clicked.connect(lambda: mainWindow.scanWidget.scanArea.remove_segment(int(mainWindow.addRemoveWindow.removePositionBox.text()) - 1))
        
        
        mainWindow.connectAction.triggered.connect(mainWindow.connectWindow.show)
        
        mainWindow.connectWindow.controlConnectBtn.clicked.connect(mainWindow.connectWindow.connect_control)
        mainWindow.connectWindow.controlDisconnectBtn.clicked.connect(mainWindow.connectWindow.disconnect_control)
        mainWindow.connectWindow.dataConnectBtn.clicked.connect(mainWindow.connectWindow.connect_data)
        mainWindow.connectWindow.dataDisconnectBtn.clicked.connect(mainWindow.connectWindow.disconnect_data)
        mainWindow.connectWindow.dataThread.updateSignal.connect(mainWindow.dataWindow.dataPlot.update)
        mainWindow.connectWindow.dataThread.textSignal.connect(mainWindow.textWidget.appendPlainText)
        
        
        mainWindow.dataSettingsAction.triggered.connect(mainWindow.dataSettingsWindow.show)
        
        mainWindow.dataSettingsWindow.applyBtn.clicked.connect(lambda: mainWindow.dataWindow.dataPlot.set_sample(mainWindow.dataSettingsWindow.dataSampleBox.text()))
        
        
        mainWindow.calcWindow.updated.connect(mainWindow.dataWindow.dataToolWidget.constBox.setText)
        mainWindow.calcWindow.updated.connect(mainWindow.dataWindow.displayToolWidget.constBox.setText)
        mainWindow.calcWindow.updated.emit(str(mainWindow.calcWindow.constant))
        
        mainWindow.btnWidget.runBtn.clicked.connect(mainWindow.run_scan)
        mainWindow.btnWidget.stopBtn.clicked.connect(mainWindow.stop_scan)
        mainWindow.btnWidget.downloadBtn.clicked.connect(mainWindow.download_scan)
        mainWindow.btnWidget.uploadBtn.clicked.connect(mainWindow.upload_scan)