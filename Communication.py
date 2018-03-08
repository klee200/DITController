from threading import Lock

import serial

from DataPlot import *


class SerialPort(serial.Serial):
    def __init__(self, port_choice, main_window):
        # Call parent constructor
        super(SerialPort, self).__init__(port=port_choice, baudrate=2000000, timeout=5)
        # Allow class to access announcer in main window
        self.main_window = main_window
        self.announcer = main_window.announcer
        # Create thread for constant reading from Arduino independent of writing to Arduino
        # self.read_active = True
        # self.read_thread = Thread(target=self.readThread)
        # self.read_thread.start()
        # Create thread for reading data
        self.data_lock = Lock()
        self.data_read_event = False
        self.end_data_lock = Lock()
        self.end_data_lock.acquire()
        self.data_thread = Thread(target=self.dataThread)
        self.data_thread.start()
        # self.data_active = False

    def serialWrite(self, output):
        # self.read_active = False
        self.write(output.encode('ascii'))
        # self.read_active = True

    def serialRead(self, stop_string):
        serial_read_input = []
        try:
            serial_read_input.append(self.readline().decode('ascii').strip())
            while serial_read_input[-1] != stop_string:
                serial_read_input.append(self.readline().decode('ascii').strip())
        except:
            serial_read_input.append("Serial read failed")
        return serial_read_input

    def startDataRead(self):
        try:
            self.serialWrite('R')
            serial_read_input = self.readline().decode('ascii').strip()
            self.data_read_event = True
            self.end_data_lock.release()
        except:
            serial_read_input = "Failed to start scan function"
        return serial_read_input

    def endDataRead(self, stop_string):
        try:
            self.data_read_event = False
            self.serialWrite('S')
            # sleep(self.timeout * 2)
            # with self.end_data_lock:
            self.end_data_lock.acquire()
                # pdb.set_trace()
                # while stop_string not in str(self.main_window.data_plot_thread.data) and self.in_waiting:
            data_clean_up = b''
            while stop_string not in str(data_clean_up):
                # pdb.set_trace()
                data_clean_up += self.read(self.in_waiting)
            print("clean up: " + str(data_clean_up))
            serial_read_input = stop_string
        except:
            serial_read_input = "Failed to stop scan function"
        return serial_read_input

    def dataThread(self):
        while self.is_open:
            # self.data_read_event.wait()
            with self.end_data_lock:
                data_read = b''
                while self.data_read_event:
                    # pdb.set_trace()
                    # data_read = b''
                    # if self.in_waiting:
                    data_read += self.read(self.in_waiting)
                    # while b'stop' not in data_read:
                    #     # data_read = self.read(900)
                    #     # if b'Stopping scan function' not in data_read:
                    #     data_read += self.read_until(b'stop', 0.00001)
                    #     # if not self.main_window.data_plot_thread.data_event.is_set():
                    if b'stop' in data_read:
                        self.main_window.data_plot_thread.data = data_read.strip(b'stop')
                        self.main_window.data_plot_thread.data_event.set()
                        # print([e for e in self.main_window.data_plot_thread.data])
                        # print(self.main_window.data_plot_thread.data)
                        # print(len(self.main_window.data_plot_thread.data))
                        # print(self.in_waiting)
                        data_read = b''

    # def readThread(self):
    #     while self.is_open:
    #         if self.in_waiting:
    #             # Continuously read from serial (from Arduino) to receive feedback
    #             try:
    #                 read_input = self.readline().decode('ascii').strip()
    #             except:
    #                 self.readline()
    #             start_time = time.clock()
    #             while read_input == '#':
    #                 data_length = int(self.readline().decode('ascii').strip())
    #                 print(data_length)
    #                 if data_length > 0:
    #                     self.main_window.data_plot.data = self.read(data_length * 2)
    #                     if time.clock() - start_time >= 1:
    #                         self.main_window.data_plot.data_event.set()
    #                         start_time = time.clock()
    #                 try:
    #                     read_input = self.readline().decode('ascii').strip()
    #                     print(read_input)
    #                 except:
    #                     self.readline()
                # Announcer announces the read input
                # self.announcer.appendPlainText(read_input)
            # elif self.data_active:
            #     start_time = time.clock()
            #     data = self.read(100)
                # data_input = 0
                # while data_input is not '$':
                #     data = []
                #     while data_input is not '#':
                #         data.append(int(data_input))
                #         # print(data_input)
                #         data_input = self.read().decode('ascii')
                # if time.clock() - start_time >= 1:
                    # print(data_input)
                    # self.main_window.data_plot.updatePlotData(data)
                    # start_time = time.clock()
                    # data_input = self.read().decode('ascii')
                # print(data_input)

    # def dataThread(self):
    #     while True:
    #         with self.serial_read_lock:
    #             start_time = time.clock()
    #             while self.data_active:
    #                 data = []
    #                 for i in range(int(self.data_length)):
    #                     try:
    #                         data_input = self.read(4)
    #                         data.append(data_input)
    #                     except:
    #                         data.append(0)
    #                 print(data[0])
                            # self.announcer.appendPlainText(data_input)
                    # if len(data) >= self.data_length:
                    # if time.clock() - start_time >= 5:
                    #     self.plot_data = data
                    #     self.main_window.data_plot.data_event.set()
                    #     self.main_window.data_plot.data_event.clear()
                    #     start_time = time.clock()
                # if self.read_active:
                #     self.serial_read_condition.notify()
                #     self.serial_read_condition.wait()

