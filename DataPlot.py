from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import numpy as np
from operator import add
from time import *
from threading import Lock
import serial
import pdb
from threading import Thread, Condition, Event
from queue import *


class DataPort(serial.Serial):
    def __init__(self, port_choice, main_window):
        # Call parent constructor
        super(DataPort, self).__init__(port=port_choice)
        # Allow class to access announcer in main window
        self.main_window = main_window
        self.announcer = main_window.announcer
        # Lock for managing data
        # self.data_lock = Lock()
        # self.data_lock.acquire()
        # Thread for reading in data
        # pyqtRemoveInputHook()
        # pdb.set_trace()
        self.data_thread = DataThread(self)
        # Signal to data plot that averages has changed
        self.main_window.averages_box.textChanged.connect(self.update)
        self.data_thread.start()
        
    def update(self, value):
        try:
            self.data_thread.num_data = int(value)
        except:
            self.data_thread.num_data = 1
        
    # def startDataThread(self):
        # self.data_lock.release()
        
    # def endDataThread(self):
        # self.data_lock.acquire()
        
class DataThread(QThread):
    # Update plot signal
    update_signal = pyqtSignal(object)
    
    def __init__(self, data_port):
        super(DataThread, self).__init__()
        self.daemon = True
        self.data_port = data_port
        self.master_port = self.data_port.main_window.connection_dialog.master_serial
        self.time = clock()
        self.n = 0
        # Connect signal
        self.update_signal.connect(self.data_port.main_window.data_plot.updatePlot)
        # Structure for holding data
        self.num_data = 1
        self.max_num_data = 100
        self.data_string = [b'' for n in range(self.max_num_data)]
        self.data = [[] for n in range(self.num_data)]
        self.master_port_access = False
        self.data_plot_trigger = True
        # self.lock = Lock()
        
    def run(self):
        # n = 0
        while self.data_port.is_open:
            # if self.data_port.in_waiting:
            self.data_port.reset_input_buffer()
            while self.master_port_access:
                self.data_string[self.n] += self.data_port.read(self.data_port.in_waiting)
                if self.master_port.in_waiting:
                    self.master_port.reset_input_buffer()
                    # self.data_port.reset_input_buffer()
                    # while t == b'\x01':
                        # if self.master_port.in_waiting:
                        # try:
                            # t = self.master_port.read()
                        # self.data_string[self.n] += self.data_port.read(self.data_port.in_waiting)
                        # except:
                            # self.data_string[self.n] += self.data_port.read(self.data_port.in_waiting)
                    while self.data_port.in_waiting:
                        self.data_string[self.n] += self.data_port.read(self.data_port.in_waiting)
                    self.n = (self.n + 1) % self.max_num_data
                    print(" ")
                    print(self.n)
                    print(self.data_plot_trigger)
                    if self.data_plot_trigger:
                        data_string_slice = [self.data_string[i] for i in range(self.n - self.num_data, self.n)]
                        self.update_signal.emit(data_string_slice)
                    # print("length of", self.n, ":", len(self.data_string[self.n]))
                    # print("not read:", self.data_port.in_waiting)
                    self.data_string[self.n] = b''
    
    # def readData(self):
        # self.data_port.reset_input_buffer()
        # with self.lock:
            # while self.trigger:
                # self.data_string[self.n] += self.data_port.read(2)
            # print(len(self.data_string[self.n]))
        # print("length:", len(self.data_string[self.n]))
        # print("not read:", self.data_port.in_waiting)
        # self.n = (self.n + 1) % self.num_data
        
    # def processData(self):
        # with self.lock:
            # self.data[self.n] = [self.data_string[self.n][i * 2] + self.data_string[self.n][i * 2 + 1] * 256 for i in range(int(len(self.data_string[self.n]) / 2))]
            # next = (self.n + 1) % self.num_data
            # self.data_string[next] = b''
            # if clock() - self.time > 1:
                # self.update_signal.emit(self.data[self.n])
                # self.time = clock()
                    
class DataPlot(pg.PlotWidget):
    def __init__(self, main_window):
        super(DataPlot, self).__init__()
        self.main_window = main_window
        self.setLabel('bottom', text='Data point')
        # self.main_window.calculator_dialog.findBoundary()
        # self.constant = float(self.main_window.calculator_dialog.mass_box.text()) * float(self.main_window.calculator_dialog.frequency_box.text())**2
        # print(self.constant)
        self.setLabel('left', text='Intensity')
        self.setDownsampling(auto=True, mode='mean')
        self.setClipToView(True)

    def updatePlot(self, data_string):
        self.main_window.connection_dialog.slave_serial.data_thread.data_plot_trigger = False
        data = [[data_n[j * 2] + data_n[j * 2 + 1] * 256 for j in range(int(len(data_n) / 2))] for data_n in data_string if len(data_n) > 0]
        print(len(data))
        plot_data = [sum(i) / len(data) for i in zip(*data)]
        # data = [data_string[j * 2] + data_string[j * 2 + 1] * 256 for j in range(int(len(data_string) / 2))]
        self.plot(range(len(plot_data)), plot_data, clear = True)
        self.main_window.connection_dialog.slave_serial.data_thread.data_plot_trigger = True

# class DataPlotThread(Thread):
    # def __init__(self):
        # super(DataPlotThread, self).__init__()
        # self.daemon = True
        # self.data = []
        # Create time axis label
        # self.plot = pg.PlotWidget()
        # self.plot.setLabel('bottom', text='Data point')
        # self.plot.setLabel('left', text='Intensity')
        # self.plot.setDownsampling(auto=True, mode='mean')
        # self.plot.setClipToView(True)
        # Thread for updating plot
        # self.plot_event = Event()
        # self.updatePlotThread = Thread(target=self.updatePlot)
        # self.updatePlotThread.start()

    # def updatePlotData(self, data):
    #     # self.data = [elem for elem in data]
    #     self.data = data
    #     # pdb.set_trace()
    #     # for point_index in range(int(len(data) / 2)):
    #     #     hb = data[point_index * 2]
    #     #     lb = data[point_index * 2 + 1]
    #     #     self.data.append(hb * 256 + lb)
    #     # self.clear()
    #     # self.plot(range(len(self.data)), self.data)
    #     self.data_event.set()
    
    # def run(self):
        # start_time = clock()
        # while True:
            # self.data_event.wait()
            # if clock() - start_time >= 1:
                # self.updatePlot()
                # plot_data = [] #np.array([e * 256 for e in self.data[0:len(self.data):2]]) + np.array([e for e in self.data[1:len(self.data):2]])
                # hb = True
                # for index in range(int(len(self.data) / 2)):
                    # plot_data.append(self.data[index * 2] * 256 + self.data[index * 2 + 1])
                #     if hb:
                #         high_byte = byte
                #         hb = False
                #     else:
                #         low_byte = byte
                #         plot_data.append(high_byte * 256 + low_byte)
                #         hb = True
            # plot_data = q.get()
            # self.plot.clear()
            # self.plot.plot(range(len(plot_data)), plot_data)
                # start_time = clock()
            # self.data_event.clear()
