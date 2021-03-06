from PyQt5.QtCore import QThread, pyqtSignal
from serial import Serial, SerialException
# import pdb


class ControlPort(Serial):
    def __init__(self):
        super(ControlPort, self).__init__(baudrate=2000000, timeout=5)

    def serial_write(self, output):
        self.write(output.encode('ascii'))

    def serial_read(self, stopString):
        readInput = []
        try:
            readInput.append(self.readline().decode('ascii').strip())
            while readInput[-1] != stopString and readInput[-1] != "":
                readInput.append(self.readline().decode('ascii').strip())
        except SerialException:
            readInput.append("Serial read failed")
        return readInput
        
class DataPort(Serial):
    def __init__(self, controlPort):
        super(DataPort, self).__init__()
        
class DataThread(QThread):
    dataSignal = pyqtSignal(object)
    textSignal = pyqtSignal(object)
    
    def __init__(self, controlPort, dataPort):
        super(DataThread, self).__init__()
        self.daemon = True
        
        self.dataPort = dataPort
        self.controlPort = controlPort
        
        self.n = 0
        # self.numData = 1
        self.maxNumData = 100
        self.dataString = [b'' for n in range(self.maxNumData)]
        # self.data = [[] for n in range(self.numData)]
        
        self.controlPortAccess = False
        self.dataPortAccess = False
                    
    def run(self):
        while self.controlPortAccess:
            if self.controlPort.in_waiting:
                self.textSignal.emit(self.controlPort.read(self.controlPort.in_waiting).decode('ascii').strip())
                if self.dataPortAccess:
                    while self.dataPort.in_waiting:
                        self.dataString[self.n] += self.dataPort.read(self.dataPort.in_waiting)
                    # if self.dataPlotTrigger:
                    self.dataSignal.emit(self.dataString[self.n].strip(b'stop'))
                    self.n = (self.n + 1) % self.maxNumData
                    self.dataString[self.n] = b''
                    self.dataPort.reset_input_buffer()
            if self.dataPortAccess:
                if self.dataPort.in_waiting:
                    self.dataString[self.n] += self.dataPort.read(self.dataPort.in_waiting)