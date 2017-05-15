import serial
import threading
import pdb

class SerialPort(serial.Serial):
    def __init__(self, port_choice, announcer):
        # Call parent constructor
        super(SerialPort, self).__init__(port=port_choice, baudrate=115200)
        # Allow class to access announcer in main window
        self.announcer = announcer
        # Create thread for constant reading from Arduino independent of writing to Arduino
        self.read_thread = threading.Thread(target=self.readThread)
        self.read_thread.start()

    def readThread(self):
        while 1:
            # Continuously read from serial (from Arduino) to receive feedback
            input = self.readline().decode('ascii').strip('\r\n')
            if input is not '':
                # Announcer announces the read input
                self.announcer.appendPlainText(input)

    def serialWrite(self, output):
        self.write(output.encode('ascii'))
