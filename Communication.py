import json
import serial
import threading
import pdb

# Function for converting scan function to json string
def convertToJson(scan_function):
    # Make dictionary for scan list
    scan_function_dict = {}
    scan_function_dict['Data'] = []
    # Create list of segment parameters with name labels
    for segment in scan_function.scan_list:
        # Dictionary to hold segment parameters
        segment_data = {}
        # Write name to dictionary
        segment_data['Name'] = segment.name_box.text()
        # Write duration to dictionary
        segment_data['Duration'] = float(segment.duration_box.text())

        # Write output 1 parameters to dictionary
        segment_data['Output 1'] = {}
        for row in range(segment.output1_table.rowCount()):
            # If putting type into dictionary, use type member variable
            if segment.output1_table.item(row, 0).text() == "Type":
                segment_data['Output 1'][segment.output1_table.item(row, 0).text()] = segment.output1_table.cellWidget(row, 1).currentText()
            # All other parameters are numbers that can be read from the table
            else:
                try:
                    segment_data['Output 1'][segment.output1_table.item(row, 0).text()] = float(segment.output1_table.cellWidget(row, 1).text())
                except:
                    segment_data['Output 1'][segment.output1_table.item(row, 0).text()] = None

        # Write output 2 parameters to dictionary
        segment_data['Output 2'] = {}
        for row in range(segment.output2_table.rowCount()):
            # If putting type into dictionary, use type member variable
            if segment.output2_table.item(row, 0).text() == "Type":
                segment_data['Output 2'][segment.output2_table.item(row, 0).text()] = segment.output2_table.cellWidget(row, 1).currentText()
            # All other parameters are numbers that can be read from the table
            else:
                try:
                    segment_data['Output 2'][segment.output2_table.item(row, 0).text()] = float(segment.output2_table.cellWidget(row, 1).text())
                except:
                    segment_data['Output 2'][segment.output2_table.item(row, 0).text()] = None

        # Write output 3 parameters to dictionary
        segment_data['Output 3'] = {}
        for row in range(segment.output3_table.rowCount()):
            # If putting type into dictionary, use type member variable
            if segment.output3_table.item(row, 0).text() == "Type":
                segment_data['Output 3'][segment.output3_table.item(row, 0).text()] = segment.output3_table.cellWidget(row, 1).currentText()
            # All other parameters are numbers that can be read from the table
            else:
                try:
                    segment_data['Output 3'][segment.output3_table.item(row, 0).text()] = float(segment.output3_table.cellWidget(row, 1).text())
                except:
                    segment_data['Output 3'][segment.output3_table.item(row, 0).text()] = None

        # Read analog values from table
        segment_data['Analog'] = []
        for row in range(segment.analog_table.rowCount()):
            try:
                segment_data['Analog'].append(float(segment.analog_table.cellWidget(row, 1).text()))
            except:
                segment_data['Analog'].append(None)

        # Read digital values from table
        segment_data['Digital'] = []
        for row in range(segment.digital_table.rowCount()):
            try:
                segment_data['Digital'].append(segment.digital_table.cellWidget(row, 1).currentText())
            except:
                segment_data['Digital'].append(None)

        # Append segment data into data list
        scan_function_dict['Data'].append(segment_data)

    # Dump json-like list into actual json object and return it
    return json.dumps(scan_function_dict, sort_keys=True)

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
