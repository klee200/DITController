from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import pyqtgraph as pg
import numpy as np
from time import *
import pdb
from threading import Thread, Condition, Event

# class DataPlot(Thread):
#     def __init__(self):
#         super(DataPlot, self).__init__()
#         self.plot = pg.PlotWidget()
#         self.data = []
#         self.plot.setLabel('bottom', text='Data point')
#         self.plot.setLabel('left', text='Intensity')
#         # Thread for updating plot
#         self.data_event = Event()
#
#     # def updatePlotData(self, data):
#     #     self.data = data
#     #     self.data_event.set()
#
#     def run(self):
#         while True:
#             self.data_event.wait()
#             plot_data = []
#             hb = True
#             for byte in self.data:
#                 if hb:
#                     high_byte = byte
#                     hb = False
#                 else:
#                     low_byte = byte
#                     plot_data.append(high_byte * 256 + low_byte)
#                     hb = True
#             self.plot.clear()
#             self.plot.plot(range(len(plot_data)), plot_data)
#             self.data_event.clear()

class DataPlotThread(Thread):
    def __init__(self):
        super(DataPlotThread, self).__init__()
        self.data = b''
        # Create time axis label
        self.plot = pg.PlotWidget()
        self.plot.setLabel('bottom', text='Data point')
        self.plot.setLabel('left', text='Intensity')
        self.plot.setDownsampling(auto=True, mode='mean')
        self.plot.setClipToView(True)
        # Thread for updating plot
        self.data_event = Event()
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

    def run(self):
        start_time = clock()
        while True:
            self.data_event.wait()
            if clock() - start_time >= 1:
                plot_data = [] #np.array([e * 256 for e in self.data[0:len(self.data):2]]) + np.array([e for e in self.data[1:len(self.data):2]])
                # hb = True
                for index in range(int(len(self.data) / 2)):
                    plot_data.append(self.data[index * 2] * 256 + self.data[index * 2 + 1])
                #     if hb:
                #         high_byte = byte
                #         hb = False
                #     else:
                #         low_byte = byte
                #         plot_data.append(high_byte * 256 + low_byte)
                #         hb = True
                self.plot.clear()
                self.plot.plot(range(len(plot_data)), plot_data)
                start_time = clock()
                self.data_event.clear()
