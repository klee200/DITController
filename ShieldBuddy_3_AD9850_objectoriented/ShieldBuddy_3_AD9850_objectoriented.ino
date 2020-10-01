#include<ArduinoJson.h>
#include<Wire.h>
#include<SoftwareWire.h>
SoftwareWire Wire3(SDA1, SCL1, true, false);

bool data_acquire = false;

/* Class declarations */
// Output parameter class
class Output
{
  private:
    uint8_t output_number;
    double start_frequency;
    double end_frequency;
    double current_frequency;
    double period_squared_step;
    const static double tuning_ratio = 4294967296.0 / 125000000;
    double duty_cycle;
    uint8_t tickle_div;
    double tickle_amplitude;
    uint8_t tickle_phase;
    const static uint8_t MCP1 = 40;
    const static uint8_t MCP2 = 41;
    const static uint8_t MCP3 = 42;
    const static uint8_t wiper0 = 0;
    const static uint8_t wiper1 = 16;
  public:
    Output(uint8_t output_index, JsonObject& parameters, uint32_t num_frequency_steps);
    ~Output() {};
    void print();
    void updateDutyCycle();
    void updateTickle();
    void chooseSPIOutput();
    uint32_t nextFrequency();
    void resetFrequency();
    void updateFrequency(uint32_t frequency);
    uint32_t getFrequency();
};

// Class Initializer. Receives index value 0-2 to differentiate the three outputs on the controller,
// list of parameters as a JsonObject, and the number of frequency steps for a frequency ramp. Initializes
// all output variables and checks if they are appropriate numbers. If not appropriate the parameter is set
// as 0.
Output::Output(uint8_t output_index, JsonObject& parameters, uint32_t num_frequency_steps)
{
  output_number = output_index + 1;
  start_frequency = parameters["Start"];		// Frequency at beginning of ramp
  end_frequency = parameters["End"];			// Frequency at end of ramp
  // The frequency is ramped according to the square of its inverse (the period),
  // so the change in period-squared is calculated.
  period_squared_step = (1 / pow(end_frequency, 2) - 1 / pow(start_frequency, 2)) / num_frequency_steps;
  current_frequency = 1 / sqrt(1 / pow(start_frequency, 2) - period_squared_step);	// Keeps track of frequency during ramp.
  
  // Parse duty cycle from parameters JsonObject and check that it's a valid number.
  duty_cycle = parameters["Duty Cycle"];
  if(duty_cycle != duty_cycle)
  {
    duty_cycle = 0;
  }
  
  // Parse tickle amplitude from parameters and check that it's a valid number.
  tickle_amplitude = parameters["Amplitude"];
  if(tickle_amplitude != tickle_amplitude)
  {
    tickle_amplitude = 0;
  }
  
  // Tickle phase is not implemented.
  tickle_phase = parameters["Phase"];
  if(tickle_phase != tickle_phase)
  {
    tickle_phase = 0;
  }
  
  // Parse tickle division from parameters. Can be divide by 2, 4, 8, 16.
  // Used for resonance ejection at different q values.
  // Or the tickle can come from Output #3 for a non-frequency locked tickle.
  // Used for CID at a specific q value.
  const char* tickle = parameters["Tickle"];
  if(strcmp(tickle, "Div / 2") == 0)
  {
    tickle_div = 2;
  }
  else if(strcmp(tickle, "Div / 4") == 0)
  {
    tickle_div = 4;
  }
  else if(strcmp(tickle, "Div / 8") == 0)
  {
    tickle_div = 8;
  }
  else if(strcmp(tickle, "Div / 16") == 0)
  {
    tickle_div = 16;
  }
  else if(strcmp(tickle, "Output 3") == 0)
  {
    tickle_div = 0;
  }
  else
  {
    tickle_div = 2;
  }
}

// Function that prints parameters to the computer screen when user asks to
// Upload the scan function.
void Output::print()
{
  SerialASC.println("--------------------------------------------------");
  SerialASC.print("Output:\t\t"); SerialASC.println(output_number);
  SerialASC.print("Start Frequency:\t"); SerialASC.println(start_frequency);
  SerialASC.print("End Frequency:\t\t"); SerialASC.println(end_frequency);
  SerialASC.print("Duty Cycle:\t\t"); SerialASC.println(duty_cycle);
  SerialASC.print("Tickle:\t\t"); SerialASC.println(tickle_div);
  SerialASC.print("Tickle Amplitude:\t"); SerialASC.println(tickle_amplitude);
  SerialASC.print("Tickle Phase:\t\t"); SerialASC.println(tickle_phase);
}

// Converts duty cycle parameter value 0-100 to a 8-bit number for the
// digital potentiometer that sets the duty cycle on the controller board.
uint8_t dutyCycleToAnalog(double duty_cycle)
{
  uint8_t analog_value = duty_cycle * 255 / 100;
  return analog_value;
}

// Tells the digital potentiometer to update the duty cycle
// over I2C using the Wire3 pins defined at the top of the code.
void Output::updateDutyCycle()
{
  // Each output has a different potentiometer. Addresses are stored
  // as MCP1, MCP2, MCP3.
  switch(output_number)
  {
    case 1:
      Wire3.beginTransmission(MCP1);
      break;
    case 2:
      Wire3.beginTransmission(MCP2);
      break;
    case 3:
      Wire3.beginTransmission(MCP3);
      break;
  }
  // wiper0 chooses the first potentiometer output which
  // controls duty cycle
  Wire3.write(wiper0);
  Wire3.write(dutyCycleToAnalog(duty_cycle));
  Wire3.endTransmission(false);
}

// Converts tickle amplitude 0-5 V to 8-bit number for
// the potentiometer.
uint8_t amplitudeToAnalog(double tickle_amplitude)
{
  uint8_t analog_value = (5 - tickle_amplitude) * 255 / 5;
  return analog_value;
}

// Updates tickle division and amplitude.
void Output::updateTickle()
{
  // Tickle division is controlled by digital outputs from the
  // ShieldBuddy. Each tickle output has three assigned digital
  // outputs. The first is LOW when using a division and HIGH when
  // using Output 3's tickle. The other two choose which value to
  // divide by with different combinations of LOW and HIGH.
  switch(output_number)
  {
    case 1:
      switch(tickle_div)
      {
        case 2:
          Fast_digitalWrite(33, LOW);
          Fast_digitalWrite(25, LOW);
          Fast_digitalWrite(26, LOW);
          break;
        case 4:
          Fast_digitalWrite(33, LOW);
          Fast_digitalWrite(25, HIGH);
          Fast_digitalWrite(26, LOW);
          break;
        case 8:
          Fast_digitalWrite(33, LOW);
          Fast_digitalWrite(25, LOW);
          Fast_digitalWrite(26, HIGH);
          break;
        case 16:
          Fast_digitalWrite(33, LOW);
          Fast_digitalWrite(25, HIGH);
          Fast_digitalWrite(26, HIGH);
          break;
        case 0:
          Fast_digitalWrite(33, HIGH);
          break;
      }
      Wire3.beginTransmission(MCP1);
      break;
    case 2:
      switch(tickle_div)
      {
        case 2:
          Fast_digitalWrite(34, LOW);
          Fast_digitalWrite(28, LOW);
          Fast_digitalWrite(29, LOW);
          break;
        case 4:
          Fast_digitalWrite(34, LOW);
          Fast_digitalWrite(28, HIGH);
          Fast_digitalWrite(29, LOW);
          break;
        case 8:
          Fast_digitalWrite(34, LOW);
          Fast_digitalWrite(28, LOW);
          Fast_digitalWrite(29, HIGH);
          break;
        case 16:
          Fast_digitalWrite(34, LOW);
          Fast_digitalWrite(28, HIGH);
          Fast_digitalWrite(29, HIGH);
          break;
        case 0:
          Fast_digitalWrite(34, HIGH);
          break;
      }
      Wire3.beginTransmission(MCP2);
      break;
	// Output 3 always has its own tickle, so there are only
	// two digital outputs to choose the division value.
    case 3:
      switch(tickle_div)
      {
        case 2:
          Fast_digitalWrite(31, LOW);
          Fast_digitalWrite(32, LOW);
          break;
        case 4:
          Fast_digitalWrite(31, HIGH);
          Fast_digitalWrite(32, LOW);
          break;
        case 8:
          Fast_digitalWrite(31, LOW);
          Fast_digitalWrite(32, HIGH);
          break;
        case 16:
          Fast_digitalWrite(31, HIGH);
          Fast_digitalWrite(32, HIGH);
          break;
      }
      Wire3.beginTransmission(MCP3);
      break;
  }
  // Addresses for the potentiometer are the same as with the duty cycle.
  // wiper1 chooses the second potentiometer output which controls tickle
  // amplitude.
  Wire3.write(wiper1);
  Wire3.write(amplitudeToAnalog(tickle_amplitude));
  Wire3.endTransmission(false);
}

// Two ShieldBuddy digital outputs control which waveform
// output will receive instructions for changing frequency over SPI.
void Output::chooseSPIOutput()
{
  switch(output_number)
  {
    case 1:
      Fast_digitalWrite(22, LOW);
      Fast_digitalWrite(23, LOW);
      break;
    case 2:
      Fast_digitalWrite(22, HIGH);
      Fast_digitalWrite(23, LOW);
      break;
    case 3:
      Fast_digitalWrite(22, LOW);
      Fast_digitalWrite(23, HIGH);
      break;
  }
}

// Resets the frequency to one step before the start frequency.
void Output::resetFrequency()
{
  current_frequency = 1 / sqrt(1 / pow(start_frequency, 2) - period_squared_step);
}

// Calculates the next frequency using the period-squared step.
uint32_t Output::nextFrequency()
{
  current_frequency = 1 / sqrt(1 / pow(current_frequency, 2) + period_squared_step);
  if(current_frequency != current_frequency)
  {
    current_frequency = 0;
  }
  uint32_t del_phase = current_frequency * tuning_ratio;
  return del_phase;
}

// Updates the frequency.
void Output::updateFrequency(uint32_t del_phase)
{
  // Establishes connection of SPI to chosen waveform output.
  chooseSPIOutput();
  // Sends 32-bit frequency information one bit at a time.
  // Digital output 63 tells the bit (0 or 1), and 62 triggers
  // a clock to acknowledge sending and receiving the bit defined
  // by 63.
  for(uint8_t i = 0; i < 32; i++)
  {
    Fast_digitalWrite(63, del_phase & 1)
    Fast_digitalWrite(62, HIGH);
    Fast_digitalWrite(62, LOW);
    del_phase >>= 1;
  }
  // The last 8 bits tell the change in phase for the square wave.
  // Probably should always be zero.
  for(uint8_t i = 0; i < 8; i++)
  {
    Fast_digitalWrite(63, 0);
    Fast_digitalWrite(62, HIGH);
    Fast_digitalWrite(62, LOW);
  }
}

// Used to request the current frequency for debugging purposes.
uint32_t Output::getFrequency()
{
  return (uint32_t)current_frequency;
}

// Scan function segment class
class Segment
{
  private:
    const static uint8_t num_outputs = 3;
    const static int DAC1 = 76;
    const static int DAC2 = 77;
    uint32_t duration;
    bool active;
    bool record;
    uint32_t num_freq_steps;
    const static uint8_t micros_per_step = 19;
    Output* output_list[num_outputs];
    uint8_t digital[12];
    double analog[8];
  public:
    Segment(JsonObject& segment);
    ~Segment();
    uint32_t getDuration();
    bool getActive();
    bool getRecord();
    uint32_t getNumSteps();
    void print();
    void setupSegment();
    void updateAnalogValue(uint8_t analog_output, double analog_volt);
    void updateAnalog();
    void updateOutputs();
    Output* getOutput(uint8_t output);
    void run();
    void stop();
};

// Class initializer. Receives parameters as JsonObject.
Segment::Segment(JsonObject& segment)
{
  // Parse duration of the segment in ms from parameters
  duration = segment["Duration"];
  // Parse whether segment is active or not from parameters.
  if(segment["Active"] == "True")
  {
    active = true;
  }
  else
  {
    active = false;
  }
  // Parse whether to record data during this segment.
  if(segment["Record"] == "True")
  {
    record = true;
  }
  else
  {
    record = false;
  }
  // Calculates the number of frequency steps for a ramp based on the duration.
  num_freq_steps = duration * 1000 / micros_per_step;
  // Create the three Outputs for this segment.
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    JsonObject& output_parameters = segment["Outputs"][i];
    output_list[i] = new Output(i, output_parameters, num_freq_steps);
  }
  // Parse instrument digital outputs from parameters.
  for(uint8_t i = 0; i < segment["Digital"].size(); i++)
  {
    if(segment["Digital"][i] == "True")
    {
      digital[i] = 1;
    }
    else
    {
      digital[i] = 0;
    }
  }
  // Parse instrument analog outputs from parameters.
  for(uint8_t i = 0; i < segment["Analog"].size(); i++)
  {
    analog[i] = segment["Analog"][i];
    if(analog[i] != analog[i])
    {
      analog[i] = 0;
    }
  }
}

// Destructor for segment class. Deletes outputs to free up memory
// when segment is deleted.
Segment::~Segment()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    delete output_list[i];
  }
}

// Used to check the segment duration.
uint32_t Segment::getDuration()
{
  return duration;
}

// Used to check if the segment is active or not.
bool Segment::getActive()
{
  return active;
}

// Used to check if data is recorded during this segment.
bool Segment::getRecord()
{
  return record;
}

// Used to get the number of frequency steps during this segment.
uint32_t Segment::getNumSteps()
{
  return num_freq_steps;
}

// Prints the segment variables to the computer over USB when user
// asks for a scan function upload.
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

// Prepares instrumer controller outputs for this segment prior to
// the frequency ramp.
void Segment::setupSegment()
{
  // Resets frequencies and updates them before starting ramps.
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->resetFrequency();
    output_list[i]->updateFrequency(output_list[i]->nextFrequency());
  }
  // Updates analog outputs for this segment.
  for(uint8_t i = 0; i < 8; i++)
  {
    updateAnalogValue(i, analog[i]);
  }
  // Updates duty cycles for this segment.
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateDutyCycle();
  }
  // Updates tickle parameters for this segment.
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateTickle();
  }
  // Updates digital outputs for this segment.
  // Digital outputs come directly from the ShieldBuddy.
  Fast_digitalWrite(42, digital[0]);
  Fast_digitalWrite(43, digital[1]);
  Fast_digitalWrite(44, digital[2]);
  Fast_digitalWrite(45, digital[3]);
  Fast_digitalWrite(46, digital[4]);
  Fast_digitalWrite(47, digital[5]);
  Fast_digitalWrite(48, digital[6]);
  Fast_digitalWrite(49, digital[7]);
  Fast_digitalWrite(50A, digital[8]);
  Fast_digitalWrite(51A, digital[9]);
  Fast_digitalWrite(52A, digital[10]);
  Fast_digitalWrite(53A, digital[11]);
  // Triggers all analog outputs to update simultaneously,
  // closely followed by all waveform frequencies being updated
  // nearly simultaneously.
  updateAnalog();
  updateOutputs();
}

// Analog outputs are controlled by digital to analog converters (DAC).
// This function stores values in DAC memory but does not change the DAC
// outputs.
void Segment::updateAnalogValue(uint8_t analog_output, double analog_volt)
{
  // First four analog outputs 0-3 are controlled by DAC1
  if (analog_output < 4)
  {
    Wire.beginTransmission(DAC1);			// Call address stored as DAC1
	// DAC has four channels identified as 0, 2, 4, 6
    Wire.write((analog_output % 4) * 2);
    Wire.write(highByte(voltToAnalog(analog_volt)));
    Wire.write(lowByte(voltToAnalog(analog_volt)));
    Wire.endTransmission(false);
  }
  // Last four analog outputs 4-7 are controlled by DAC2.
  else if (analog_output >= 4)
  {
    Wire.beginTransmission(DAC2);
    Wire.write((analog_output % 4) * 2);
    Wire.write(highByte(voltToAnalog(analog_volt)));
    Wire.write(lowByte(voltToAnalog(analog_volt)));
    Wire.endTransmission(false);
  }
}

// Tells all DACs to change analog outputs to values stored
// in memory.
void Segment::updateAnalog()
{
  Wire.beginTransmission(72);	// General address for DAC1 and DAC2.
  Wire.write(48);				// Tells all four DAC outputs to change.
  Wire.write(1);
  Wire.write(1);
  Wire.endTransmission(false);
}

// Calculates 16-bit instruction for DAC from desired
// analog output value.
uint16_t voltToAnalog(double volt)
{
  uint16_t analog_value = volt * 3281 + 33379;
  return analog_value;
}

// Updates all waveform outputs nearly simultaneously.
void Segment::updateOutputs()
{
  Fast_digitalWrite(9, HIGH);
  Fast_digitalWrite(7, HIGH);
  Fast_digitalWrite(5, HIGH);
  Fast_digitalWrite(9, LOW);
  Fast_digitalWrite(7, LOW);
  Fast_digitalWrite(5, LOW);
}

// Used to check parameters of the waveform outputs.
Output* Segment::getOutput(uint8_t output)
{
  return output_list[output];
}

// Updates frequencies of all three waveform outputs.
// This function is called repeatedly during a frequency ramp.
void Segment::run()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateFrequency(output_list[i]->nextFrequency());
  }
  updateOutputs();
}

// Sets all digital and analog outputs and frequencies to zero
// when user tells scan function to stop.
void Segment::stop()
{
  for(uint8_t i = 0; i < 12; i++)
  {
    digitalWrite(i + 42, LOW);
  }
  for(uint8_t i = 0; i < 8; i++)
  {
    updateAnalogValue(i, 0);
  }
  updateAnalog();
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateFrequency(0);
  }
  updateOutputs();
}

// Scan function class - container for the scan function segment objects
class ScanFunction
{
  private:
    uint8_t current_size;
    const static uint8_t max_size = 20;
    Segment* segment_list[max_size];
  public:
    ScanFunction();
    ~ScanFunction() {};
    void addSegment(JsonObject& segment);
    uint32_t getSegmentDuration(uint8_t segment_index);
    bool getSegmentRecord(uint8_t segment_index);
    uint8_t size();
    void print();
    void clear();
    void run();
    void stop();
};

// Scan function initialized with a size of 0.
ScanFunction::ScanFunction()
{
  current_size = 0;
}

// Creates a new segment from the parameters JsonObject.
void ScanFunction::addSegment(JsonObject& segment)
{
  // Maximum size of scan function is 20 to protect memory.
  if(current_size < max_size)
  {
    Segment* new_segment = new Segment(segment);
	// Checks if segment is defined as active.
	// If not, it gets deleted from memory.
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

// Used to check the duration of a chosen segment.
uint32_t ScanFunction::getSegmentDuration(uint8_t segment_index)
{
  return segment_list[segment_index]->getDuration();
}

// Used to check if data is recorded during a chosen segment.
bool ScanFunction::getSegmentRecord(uint8_t segment_index)
{
  return segment_list[segment_index]->getRecord();
}

// Used to check the size of the scan function.
uint8_t ScanFunction::size()
{
  return current_size;
}

// Prints the scan function parameters to computer when user asks to upload scan function.
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

// Deletes all segments to clear memory for a new scan function.
// Resets size to 0.
void ScanFunction::clear()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    delete segment_list[i];
  }
  current_size = 0;
}

// Runs scan function segments in order.
void ScanFunction::run()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
	// Updates outputs for new segment before starting frequency ramp.
    segment_list[i]->setupSegment();
	// Check number of frequency steps for ramp.
    uint32_t num_steps = segment_list[i]->getNumSteps();
	// If recording during this segment trigger Arduino Due to start
	// sending data to computer with ShieldBuddy digital pin 13.
    if(segment_list[i]->getRecord())
    {
      Fast_digitalWrite(13, 1);
    }
	// Iterate through the number of frequency steps.
	// Update frequencies at each iteration.
    for(uint32_t j = 0; j < num_steps; j++)
    {
      segment_list[i]->run();
    }
	// If recording during this segment trigger Arduino Due to stop
	// sending data to computer.
    if(segment_list[i]->getRecord())
    {
      Fast_digitalWrite(13, 0);
	  // Prints final frequency of waveform output 2 to computer.
	  // Useful for checking if frequency ramp ended at correct end frequency.
      SerialASC.print(segment_list[i]->getOutput(1)->getFrequency());
    }
  }
}

// Stops scan function.
void ScanFunction::stop()
{
  if(current_size > 0)
  {
    segment_list[0]->stop();
  }
}

/*** Don't worry, the normal Arduino setup() and loop() are below this block! ***/

/* LMU uninitialised data */
StartOfUninitialised_LMURam_Variables
/* Put your LMU RAM fast access variables that have no initial values here e.g. uint32 LMU_var; */
EndOfUninitialised_LMURam_Variables

/* LMU uninitialised data */
StartOfInitialised_LMURam_Variables
/* Put your LMU RAM fast access variables that have an initial value here e.g. uint32 LMU_var_init = 1; */
EndOfInitialised_LMURam_Variables

/* If you do not care where variables end up, declare them here! */
const uint32_t SERIAL_RATE = 2000000;
const uint16_t SERIAL_TIMEOUT = 5000;
const uint16_t MAX_INPUT_LENGTH = 10000;
ScanFunction scan_function;


/*** Core 0 ***/

void setup() {
  // put your setup code for core 0 here, to run once:
  SerialASC.begin(SERIAL_RATE);				// Start USB connection with computer.
  SerialASC.setTimeout(SERIAL_TIMEOUT);		// USB communication will give up after 5 s.
  // ShieldBuddy pins 62 and 63 are for SPI communication with waveform outputs.
  pinMode(62, OUTPUT);
  pinMode(63, OUTPUT);
  // Wire3 is I2C communication with potentiometers for duty cycle
  // and tickle amplitude.
  Wire3.begin();
  Wire3.setClock(152435);
  // Wire is I2C communication with DACs for controller analog outputs.
  Wire.setWireBaudrate(400000);
  Wire.begin();
  // ShieldBuddy pins used for controller digital outputs.
  for(int i = 22; i < 54; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  // ShieldBuddy pins used for establishing connections with the different
  // waveform outputs.
  for(int i = 4; i < 12; i++)
  {
    pinMode(i, OUTPUT);
  }
  Fast_digitalWrite(10, HIGH);	// Disconnected, needs to be HIGH for some reason.
  // The following prepares waveform outputs for use.
  // They are each reset, told to acknowledge receipt of a new frequency (even though
  // none was sent), and then updated.
  Fast_digitalWrite(8, HIGH);	// Resets waveform output 1
  Fast_digitalWrite(8, LOW);
  Fast_digitalWrite(22, LOW);	// Establish connection with waveform output 1.
  Fast_digitalWrite(23, LOW);
  Fast_digitalWrite(62, HIGH);	// Trigger frequency data acknowledge.
  Fast_digitalWrite(62, LOW);
  Fast_digitalWrite(9, HIGH);	// Update waveform output 1.
  Fast_digitalWrite(9, LOW);
  Fast_digitalWrite(6, HIGH);	// Resets waveform output 2.
  Fast_digitalWrite(6, LOW);
  Fast_digitalWrite(22, HIGH);	// Establish connection with waveform output 2.
  Fast_digitalWrite(23, LOW);
  Fast_digitalWrite(62, HIGH);	// Data acknowledge
  Fast_digitalWrite(62, LOW);
  Fast_digitalWrite(7, HIGH);	// Update waveform output 2.
  Fast_digitalWrite(7, LOW);
  Fast_digitalWrite(4, HIGH);	// Resets waveform output 3.
  Fast_digitalWrite(4, LOW);
  Fast_digitalWrite(22, LOW);	// Establish connection with waveform output 3.
  Fast_digitalWrite(23, HIGH);
  Fast_digitalWrite(62, HIGH);	// Data acknowledge
  Fast_digitalWrite(62, LOW);
  Fast_digitalWrite(5, HIGH);	// Update waveform output 3.
  Fast_digitalWrite(5, LOW);
  
  SerialASC.println("Setup complete");
}


void loop()
{
  // Check is computer is saying something.
  if(SerialASC.available())
  {
	// Computer will send a letter depending on which button was clicked.
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
  
  // ShieldBuddy pin 13 used to trigger Arduino Due for data collection.
  // This could be in the normal setup.
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
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



/* Controller functions */
// Downloads scan parameters from computer.
void downloadScan()
{
  SerialASC.println("Download initiated");
  scan_function.clear();
  SerialASC.read();			// Read opening '[' from json array before parsing objects
  char next_char = ','; 	// Comma separates json objects in array
  while(next_char == ',')
  {
	// Create buffer for holding parameters until scan function is made.
    StaticJsonBuffer<MAX_INPUT_LENGTH> json_buffer;
	// Parse a segment.
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
    if(next_char == ']'){SerialASC.println("Download successful");}
  }
  while(SerialASC.available()){SerialASC.read();} // Clear input buffer
  SerialASC.println(scan_function.size());
  SerialASC.println("Download finished");
  return;
}

// Sends scan function back to computer. Checks if scan function was downloaded correctly.
void uploadScan()
{
  SerialASC.println("Upload initiated");
  scan_function.print();
  SerialASC.println("Upload finished");
  return;
}

// Start scan function.
void runScan()
{
  SerialASC.println("Running scan function");
  char choice = ' ';
  // Keep checking for a stop signal from computer.
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

// Stops scan function.
void stopScan()
{
  SerialASC.println("Stopping scan function");
  scan_function.stop();
  return;
}
