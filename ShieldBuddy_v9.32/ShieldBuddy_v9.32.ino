#include<ArduinoJson.h>
//#include<SPI.h>
#include<Wire.h>
#include<SoftwareWire.h>
SoftwareWire Wire2(SDA1, SCL1, true, false);
//SoftwareWire Wire2(21, 20, true, false);


/*******************************************************************************************************
************************              Output class          ********************************************
*******************************************************************************************************/
class Output
{
  private:
  
    uint8_t output_number;
    
    double start_frequency;
    double end_frequency;
    double current_frequency;
    double period_squared_step;
    const static double tuning_ratio = 4294967296.0 / 125000000;
    
    uint8_t DAC_address;
    double duty_cycle;
    double amplitude;
    
  public:

    Output(uint8_t output_index);
    Output(uint8_t output_index, JsonObject& parameters, uint32_t num_frequency_steps);
    ~Output() {};
    
    void print();
    void run();
    void reset();

    void setupOutput();
    
    double getFrequency();
    void resetFrequency();
    void nextFrequency();
    void updateFrequency();
    void switchSPI();
    
    void updateDutyCycle();
    void updateAmplitude();
};

// Default Ouptut constructor for stopping scan function
Output::Output(uint8_t output_index)
{
  output_number = output_index + 1;
  start_frequency = 0;
  end_frequency = 0;
  current_frequency = 0;
  duty_cycle = 0;
  amplitude = 0;
}

// Output Constructor
Output::Output(uint8_t output_index, JsonObject& parameters, uint32_t num_frequency_steps)
{
  output_number = output_index + 1;
  
  start_frequency = parameters["Start"];
  end_frequency = parameters["End"];
  period_squared_step = (1 / pow(end_frequency, 2) - 1 / pow(start_frequency, 2)) / num_frequency_steps;
  current_frequency = 1 / sqrt(1 / pow(start_frequency, 2) - period_squared_step);
  
  DAC_address = 76 + output_index;
  duty_cycle = parameters["Duty Cycle"];
  if(duty_cycle != duty_cycle){duty_cycle = 0;}
  amplitude = parameters["Amplitude"];
  if(amplitude != amplitude){amplitude = 0;}
}

// Print Output parameters to USB Serial
void Output::print()
{
  SerialASC.println("--------------------------------------------------");
  SerialASC.print("Output:\t\t"); SerialASC.println(output_number);
  SerialASC.print("Start Frequency:\t"); SerialASC.println(start_frequency);
  SerialASC.print("End Frequency:\t\t"); SerialASC.println(end_frequency);
  SerialASC.print("Duty Cycle:\t\t"); SerialASC.println(duty_cycle);
  SerialASC.print("Tickle Amplitude:\t"); SerialASC.println(amplitude);
}

// Updates current frequency and sends it to waveform chip through SPI
void Output::run()
{
  nextFrequency();
  updateFrequency();
}

// Reset phase to zero
void Output::reset()
{
  switchSPI();
  Fast_digitalWrite(13, HIGH);
  Fast_digitalWrite(13, LOW);
}

// Setup start frequency, duty cycle, and amplitude
void Output::setupOutput()
{
  resetFrequency();
  updateDutyCycle();
  updateAmplitude();
}

// Returns current frequency, for troubleshooting
double Output::getFrequency()
{
  return current_frequency;
}

// Resets current frequency variable to starting frequency
void Output::resetFrequency()
{
  current_frequency = start_frequency;
}

// Changes current frequency to next frequency in ramp
void Output::nextFrequency()
{
  current_frequency = 1 / sqrt(1 / pow(current_frequency, 2) + period_squared_step);
}

// Calculates tuning word for waveform chip, switches the SPI line to the current waveform chip, and sends the frequency information
void Output::updateFrequency()
{
  if(current_frequency != current_frequency){current_frequency = 0;}
  uint32_t del_phase = current_frequency * tuning_ratio;
  switchSPI();
  for(uint8_t i = 0; i < 32; i++)
  {
    Fast_digitalWrite(11, del_phase & 1)
    Fast_digitalWrite(13, HIGH);
    Fast_digitalWrite(13, LOW);
    del_phase >>= 1;
  }
  for(uint8_t i = 0; i < 8; i++)
  {
    Fast_digitalWrite(11, 0);
    Fast_digitalWrite(13, HIGH);
    Fast_digitalWrite(13, LOW);
  }
}

// Switches SPI communication lines to current waveform chip
void Output::switchSPI()
{
  uint8_t output_index = output_number - 1;
  Fast_digitalWrite(8, output_index & 1);
  output_index >>= 1;
  Fast_digitalWrite(9, output_index & 1);
}

// Function for calculating duty cycle DAC value
uint16_t dutyCycleToDAC(double duty_cycle)
{
  uint16_t analog_value = (100 - duty_cycle) / 100 * 65535;
  return analog_value;
}

// Calculates duty cycle DAC value and sends it to DAC
void Output::updateDutyCycle()
{
  uint16_t DAC_value = dutyCycleToDAC(duty_cycle);
  Wire.beginTransmission(DAC_address);
  Wire.write(6); // Duty cycle controlled by 3rd DAC channel
  Wire.write(highByte(DAC_value));
  Wire.write(lowByte(DAC_value));
  Wire.endTransmission();
}

// Function for calculating amplitude DAC value
uint16_t amplitudeToDAC(double amplitude)
{
  uint16_t DAC_value = amplitude / 5 * 65535;
  return DAC_value;
}

// Calculates amplitude DAC value and sends it to DAC
void Output::updateAmplitude()
{
  if(amplitude == 0)
  {
    switch(output_number)
    {
      case 1:
        Fast_digitalWrite(4, LOW);
        break;
      case 2:
        Fast_digitalWrite(23, LOW);
        break;
      case 3:
        Fast_digitalWrite(27, LOW);
        break;
    }
  }
  else
  {
    switch(output_number)
    {
      case 1:
        Fast_digitalWrite(4, HIGH);
        break;
      case 2:
        Fast_digitalWrite(23, HIGH);
        break;
      case 3:
        Fast_digitalWrite(27, HIGH);
        break;
    }
    uint16_t DAC_amp = amplitudeToDAC(amplitude);
    
    Wire.beginTransmission(DAC_address);
    Wire.write(2);
    Wire.write(highByte(DAC_amp));
    Wire.write(lowByte(DAC_amp));
    Wire.endTransmission();
    
    Wire.beginTransmission(DAC_address);
    Wire.write(4);
    Wire.write(highByte(DAC_amp));
    Wire.write(lowByte(DAC_amp));
    Wire.endTransmission();
  }
}



/*******************************************************************************************************
************************              Segment class          *******************************************
*******************************************************************************************************/
class Segment
{
  private:
  
    const static uint8_t num_outputs = 3;
    const static uint8_t num_digital = 14;
    const static uint8_t num_analog = 8;
    
    const static uint8_t micros_per_step = 19;
    uint32_t duration;
    uint32_t num_freq_steps;

    bool active;
    bool record;
    
    Output* output_list[num_outputs];
    uint8_t digital[num_digital];
    double analog[num_analog];
    const static int DAC1 = 76;
    const static int DAC2 = 77;
    
  public:

    Segment();
    Segment(JsonObject& segment);
    ~Segment();
    
    void print();
    void run();
    void reset();
    
    uint32_t getDuration();
    uint32_t getNumSteps();
    bool getActive();
    bool getRecord();
    
    void setupSegment();
    
    Output* getOutput(uint8_t output);
    void updateOutputs();
    void updateDigital();
    void updateAnalog();
    void updateDAC();
};

// Default Segment constructor for stopping scan function
Segment::Segment()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i] = new Output(i);
  }
  for(uint8_t i = 0; i < num_digital; i++)
  {
    digital[i] = 0;
  }
  for(uint8_t i = 0; i < num_analog; i++)
  {
    analog[i] = 0;
  }
}

// Segment class constructor
Segment::Segment(JsonObject& segment)
{
  duration = segment["Duration"];
  num_freq_steps = duration * 1000 / micros_per_step;
  
  if(segment["Active"] == "True"){active = true;}
  else{active = false;}
  if(segment["Record"] == "True"){record = true;}
  else{record = false;}
  
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    JsonObject& output_parameters = segment["Outputs"][i];
    output_list[i] = new Output(i, output_parameters, num_freq_steps);
  }
  for(uint8_t i = 0; i < num_digital; i++)
  {
    if(i < segment["Digital"].size())
    {      
      if(segment["Digital"][i] == "True"){digital[i] = 1;}
      else{digital[i] = 0;}
    }
    else{digital[i] = 0;}
  }
  for(uint8_t i = 0; i < num_analog; i++)
  {
    if(i < segment["Analog"].size())
    {
      analog[i] = segment["Analog"][i];
      if(analog[i] != analog[i]){analog[i] = 0;}
    }
    else{analog[i] = 0;}
  }
}

// Segment class destructor, deletes output class instances
Segment::~Segment()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    delete output_list[i];
  }
}

// Returns segment duration for scan function timing
uint32_t Segment::getDuration()
{
  return duration;
}

// Returns number of frequency step for scan function timing
uint32_t Segment::getNumSteps()
{
  return num_freq_steps;
}

// Returns whether to use segment in scan function
bool Segment::getActive()
{
  return active;
}

// Returns whether to record data during this segment
bool Segment::getRecord()
{
  return record;
}

// Prints Segment parameters to USB serial
void Segment::print()
{
  SerialASC.print("Duration:\t\t"); SerialASC.println(duration);
  SerialASC.print("Frequency steps:\t"); SerialASC.println(num_freq_steps);
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    if(output_list[i] != NULL)
    {
      output_list[i]->print();
    }
    else
    {
      SerialASC.println("None");
    }
  }
}

// Updates outputs current frequencies to next frequencies and sends update signal for all
void Segment::run()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->run();
  }
  updateOutputs();
}

// Reset Output phase to zero
void Segment::reset()
{
  Fast_digitalWrite(3, HIGH);
  Fast_digitalWrite(3, LOW);
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->reset();
  }
  updateOutputs();
}

// Initializes segment before running frequency ramps
void Segment::setupSegment()
{
  // Setup Outputs
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->setupOutput();
  }
  // Analog
  updateAnalog();
  // Update Digital
  updateDigital();
  // Update together
  updateDAC();
  updateOutputs();
}

void Segment::updateDigital()
{
  Fast_digitalWrite(40, digital[0]);
  Fast_digitalWrite(41, digital[1]);
  Fast_digitalWrite(42, digital[2]);
  Fast_digitalWrite(43, digital[3]);
  Fast_digitalWrite(44, digital[4]);
  Fast_digitalWrite(45, digital[5]);
  Fast_digitalWrite(46, digital[6]);
  Fast_digitalWrite(47, digital[7]);
  Fast_digitalWrite(48, digital[8]);
  Fast_digitalWrite(49, digital[9]);
  Fast_digitalWrite(50A, digital[10]);
  Fast_digitalWrite(51A, digital[11]);
  Fast_digitalWrite(52A, digital[12]);
  Fast_digitalWrite(53A, digital[13]);
}

// Function for calculating DAC value
uint16_t voltToDAC(double volt)
{
  uint16_t DAC_value = volt / 10 * 32767 + 32767;
  return DAC_value;
}

// Updates Analog values
void Segment::updateAnalog()
{
  for(uint8_t i = 0; i < num_analog; i++)
  {
    uint16_t DAC_value = voltToDAC(analog[i]);
    if (i < 4)
    {
      Wire2.beginTransmission(DAC1);
      Wire2.write((i % 4) * 2);
      Wire2.write(highByte(DAC_value));
      Wire2.write(lowByte(DAC_value));
      Wire2.endTransmission();
    }
    else if (i >= 4)
    {
      Wire2.beginTransmission(DAC2);
      Wire2.write((i % 4) * 2);
      Wire2.write(highByte(DAC_value));
      Wire2.write(lowByte(DAC_value));
      Wire2.endTransmission();
    }
  }
}

// Tells all DACs to update channels with current stored values
void Segment::updateDAC()
{
  // Analog outputs
  Wire2.beginTransmission(72);
  Wire2.write(48);
  Wire2.write(1);
  Wire2.write(1);
  Wire2.endTransmission();
  // Frequency outputs
  Wire.beginTransmission(72);
  Wire.write(48);
  Wire.write(1);
  Wire.write(1);
  Wire.endTransmission();
}

// Tells frequency outputs to update to current stored values
void Segment::updateOutputs()
{
  Fast_digitalWrite(2, HIGH);
  Fast_digitalWrite(2, LOW);
}

// Returns Output class instance for troubleshooting
Output* Segment::getOutput(uint8_t output)
{
  return output_list[output];
}


/*******************************************************************************************************
************************        Scan Function class          *******************************************
*******************************************************************************************************/
class ScanFunction
{
  private:
  
    uint8_t current_size;
    const static uint8_t max_size = 20;
    
    Segment* segment_list[max_size];
    Segment stop_segment;
    
  public:
  
    ScanFunction();
    ~ScanFunction() {};
    
    void print();
    void clear();
    void run();
    void reset();
    void stop();
    uint8_t size();
    
    void addSegment(JsonObject& segment);
};

// Class constructor
ScanFunction::ScanFunction()
{
  current_size = 0;
}

// Print scan function parameters to USB serial
void ScanFunction::print()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    SerialASC.println("--------------------------------------------------");
    SerialASC.print("Segment:\t\t"); SerialASC.println(i + 1);
    segment_list[i]->print();
    SerialASC.println("--------------------------------------------------");
  }
}

// Delete Segments and reset size to zero
void ScanFunction::clear()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    delete segment_list[i];
  }
  current_size = 0;
}

// Run scan function
void ScanFunction::run()
{
//  reset();
  for(uint8_t i = 0; i < current_size; i++)
  {
    segment_list[i]->setupSegment();
    uint32_t num_steps = segment_list[i]->getNumSteps();
    if(segment_list[i]->getRecord())
    {
      Fast_digitalWrite(A5, 1);
    }
    for(uint32_t j = 0; j < num_steps; j++)
    {
      segment_list[i]->run();
    }
    if(segment_list[i]->getRecord())
    {
      Fast_digitalWrite(A5, 0);
      SerialASC.print(segment_list[i]->getOutput(0)->getFrequency());
    }
  }
}

// Reset phase of scan function
void ScanFunction::reset()
{
  unsigned long previous_millis = millis();
  stop_segment.reset();
  while(millis() - previous_millis <= 5);
}

// Run default segment for stopping scan function
void ScanFunction::stop()
{
  SerialASC.println("Stopping scan function");
  stop_segment.setupSegment();
  stop_segment.run();
}

// Return scan function size for control
uint8_t ScanFunction::size()
{
  return current_size;
}

// Add new Segment to Scan Function
void ScanFunction::addSegment(JsonObject& segment)
{
  if(current_size < max_size)
  {
    Segment* new_segment = new Segment(segment);
    if(new_segment->getActive())
    {
      segment_list[current_size] = new_segment;
      current_size++;
    }
    else
    {
      delete new_segment;
    }
  }
  else
  {
    SerialASC.print("Scan function length exceeds maximum size of "); SerialASC.println(max_size);
  }
}


/*****************    Global Variables **************/
ScanFunction scan_function;


/*******************************************************************************************************
************************        Controller Functions         *******************************************
*******************************************************************************************************/
void downloadScan()
{
  SerialASC.println("Download initiated");
  scan_function.clear();
  SerialASC.read(); // Read opening '[' from json array before parsing objects
  char next_char = ','; // Comma separates json objects in array
  while(next_char == ',')
  {
    StaticJsonBuffer<10000> json_buffer;
    JsonObject& scan_segment = json_buffer.parseObject(SerialASC);
    if(scan_segment.success())
    {
      scan_function.addSegment(scan_segment);
      if(SerialASC.available())
      {
        next_char = SerialASC.read(); // Check if another comma - signals there is another segment to read
      }
    }
    else
    {
      SerialASC.println("Download failed");
      next_char = '0';  // End while loop if bad segment
    }
    if(next_char == ']'){SerialASC.println("Download succesful");}
  }
  SerialASC.print("Downloaded "); SerialASC.print(scan_function.size()); SerialASC.println(" segments");
  while(SerialASC.available()){SerialASC.read();} // Clear input buffer
  SerialASC.println("Download finished");
  return;
}

void uploadScan()
{
  SerialASC.println("Upload initiated");
  scan_function.print();
  SerialASC.println("Upload finished");
  return;
}

void runScan()
{
  SerialASC.println("Running scan function");
  char choice = ' ';
  while(choice != 'S')
  {
    scan_function.run();
    if(SerialASC.available())
    {
      choice = SerialASC.read();
    }
  }
  stopScan();
  return;
}

void stopScan()
{
  scan_function.stop();
  return;
}




StartOfUninitialised_LMURam_Variables
EndOfUninitialised_LMURam_Variables

StartOfInitialised_LMURam_Variables
EndOfInitialised_LMURam_Variables


/*** Core 0 ***/

void setup() {
  // put your setup code for core 0 here, to run once:
  SerialASC.begin(2000000);
  SerialASC.setTimeout(5000);
  Wire.setWireBaudrate(400000);
  Wire.begin();
  Wire2.begin();
  for(int i = 22; i < 54; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  for(int i = 2; i < 14; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  Fast_digitalWrite(10, HIGH);
  IfxPort_setPinModeOutput(&MODULE_P10, 7, IfxPort_OutputMode_pushPull, IfxPort_OutputIdx_general);   // digital pin mode for A5, triggers Due for data collection

//  scan_function.reset();
  stopScan();
  
  SerialASC.println("Setup complete");
}


void loop()
{
  if(SerialASC.available())
  {
    char choice = SerialASC.read();
    switch(choice)
    {
      case 'D':
        downloadScan();
        break;
      case 'U':
        uploadScan();
        break;
      case 'R':
        runScan();
        break;
      case 'S':
        stopScan();
        break;
    }
  }
}







/*** Core 1 ***/

/* CPU1 Uninitialised Data */
StartOfUninitialised_CPU1_Variables
/* Put your CPU1 fast access variables that have no initial values here e.g. uint32 CPU1_var; */
//uint32_t record_duration;
EndOfUninitialised_CPU1_Variables

/* CPU1 Initialised Data */
StartOfInitialised_CPU1_Variables
/* Put your CPU1 fast access variables that have an initial value here e.g. uint32 CPU1_var_init = 1; */
EndOfInitialised_CPU1_Variables

void setup1() {
  // put your setup code for core 1 here, to run once:
}


void loop1() {

  
}


/*** Core 2 ***/

/* CPU2 Uninitialised Data */
StartOfUninitialised_CPU2_Variables
/* Put your CPU2 fast access variables that have no initial values here e.g. uint32 CPU2_var; */
EndOfUninitialised_CPU2_Variables

/* CPU2 Initialised Data */
StartOfInitialised_CPU2_Variables
/* Put your CPU2 fast access variables that have an initial value here e.g. uint32 CPU2_var_init = 1; */
EndOfInitialised_CPU2_Variables


void setup2() {
  // put your setup code for core 2 here, to run once:


}


void loop2() {
  // put your main code for core 2 here, to run repeatedly:


}



