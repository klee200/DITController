import json
import serial
import threading
import pdb

# Function for converting scan function to json string
def convertToJson(scan_list):
    # Make json-like object list
    scan_list_json = {}
    scan_list_json['data'] = []
    segment_data = {}
    # Create list of segment parameters with name labels
    for segment in scan_list:
        for row in range(segment.segment_table.rowCount()):
            # If putting type into json string, use type member variable
            if segment.segment_table.item(row, 0).text() == "Type":
                segment_data[segment.segment_table.item(row, 0).text()] = segment.type
            # All other parameters are numbers that can be read from the table
            else:
                try:
                    segment_data[segment.segment_table.item(row, 0).text()] = float(segment_data[segment.segment_table.item(row, 1).text()])
                except:
                    segment_data[segment.segment_table.item(row, 0).text()] = None
        # Read analog values from table
        segment_data['analog'] = []
        for row in range(segment.analog_table.rowCount()):
            try:
                segment_data['analog'].append(float(segment_data[segment.analog_table.item(row, 1).text()]))
            except:
                segment_data['analog'].append(None)
        # Read digital values from table
        segment_data['digital'] = []
        for row in range(segment.digital_table.rowCount()):
            try:
                segment_data['digital'].append(float(segment_data[segment.digital_table.item(row, 1).text()]))
            except:
                segment_data['digital'].append(None)
        # Append segment data into data list
        scan_list_json['data'].append(segment_data)
    scan_list_json['job'] = 'download'
    # Dump json-like list into actual json object and return it
    return json.dumps(scan_list_json, sort_keys=True)

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
