from threading import Lock
from PyQt5.QtCore import *

from serial import *
import pdb


class ControlPort(Serial):
    def __init__(self):
        super(ControlPort, self).__init__(baudrate=2000000, timeout=5)

    def serial_write(self, output):
        self.write(output.encode('ascii'))

    def serial_read(self, stopString):
        readInput = []
        try:
            readInput.append(self.readline().decode('ascii').strip())
            while readInput[-1] != stopString:
                readInput.append(self.readline().decode('ascii').strip())
        except SerialException:
            readInput.append("Serial read failed")
        return readInput
        
class DataPort(Serial):
    def __init__(self, controlPort):
        super(DataPort, self).__init__(baudrate=21000000)
        
        self.dataThread = DataThread(self, controlPort)
        
class DataThread(QThread):
    updateSignal = pyqtSignal(object)
    
    def __init__(self, dataPort, controlPort):
        super(DataThread, self).__init__()
        self.daemon = True
        
        self.dataPort = dataPort
        self.controlPort = controlPort
        
        self.n = 0
        self.numData = 1
        self.maxNumData = 100
        self.dataString = [b'' for n in range(self.maxNumData)]
        self.data = [[] for n in range(self.numData)]
        
        self.controlPortAccess = False
        self.dataPlotTrigger = True
        
    def run(self):
        while self.dataPort.is_open:
            self.dataPort.reset_input_buffer()
            while self.controlPortAccess:
                self.dataString[self.n] += self.dataPort.read(self.dataPort.in_waiting)
                if self.controlPort.in_waiting:
                    self.controlPort.reset_input_buffer()
                    while self.dataPort.in_waiting:
                        self.dataString[self.n] += self.dataPort.read(self.dataPort.in_waiting)
                    self.n = (self.n + 1) % self.maxNumData
                    print(" ")
                    print(self.n)
                    if self.dataPlotTrigger:
                        dataStringSlice = self.dataString[self.n - 1]
                        self.updateSignal.emit(dataStringSlice)
                    self.dataString[self.n] = b''