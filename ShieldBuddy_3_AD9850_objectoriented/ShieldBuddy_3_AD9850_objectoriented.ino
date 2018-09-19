#include<ArduinoJson.h>
//#include<SPI.h>
#include<Wire.h>
#include<SoftwareWire.h>
SoftwareWire Wire3(SDA1, SCL1, true, false);
SoftwareWire Wire2(21, 20, true, false);

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
    void chooseUpdateOutput();
    uint32_t nextFrequency();
    void resetFrequency();
    void updateFrequency(uint32_t frequency);
    void run();
    void stop();
};

Output::Output(uint8_t output_index, JsonObject& parameters, uint32_t num_frequency_steps)
{
  output_number = output_index + 1;
  start_frequency = parameters["Start"];
  end_frequency = parameters["End"];
  period_squared_step = (1 / pow(end_frequency, 2) - 1 / pow(start_frequency, 2)) / num_frequency_steps;
  current_frequency = 1 / sqrt(1 / pow(start_frequency, 2) - period_squared_step);
  duty_cycle = parameters["Duty Cycle"];
  if(duty_cycle != duty_cycle)
  {
    duty_cycle = 0;
  }
  tickle_amplitude = parameters["Amplitude"];
  if(tickle_amplitude != tickle_amplitude)
  {
    tickle_amplitude = 0;
  }
  const char* tickle = parameters["Tickle"];
  if(strcmp(tickle, "Drive / 2") == 0)
  {
    tickle_div = 2;
  }
  else if(strcmp(tickle, "Drive / 4") == 0)
  {
    tickle_div = 4;
  }
  else if(strcmp(tickle, "Drive / 8") == 0)
  {
    tickle_div = 8;
  }
  else if(strcmp(tickle, "Drive / 16") == 0)
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

void Output::print()
{
  SerialASC.print("Output: "); SerialASC.println(output_number);
  SerialASC.print("Start Frequency: "); SerialASC.println(start_frequency);
  SerialASC.print("End Frequency: "); SerialASC.println(end_frequency);
  SerialASC.print("Duty Cycle: "); SerialASC.println(duty_cycle);
  SerialASC.print("Tickle"); SerialASC.println(tickle_div);
  SerialASC.print("Tickle Amplitude"); SerialASC.println(tickle_amplitude);
  SerialASC.print("Tickle Phase"); SerialASC.println(tickle_phase);
}

uint8_t dutyCycleToAnalog(double duty_cycle)
{
  uint8_t analog_value = duty_cycle * 255 / 100;
  return analog_value;
}

void Output::updateDutyCycle()
{
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
  Wire3.write(wiper0);
  Wire3.write(dutyCycleToAnalog(duty_cycle));
  Wire3.endTransmission(false);
}

uint8_t amplitudeToAnalog(double tickle_amplitude)
{
  uint8_t analog_value = (5 - tickle_amplitude) * 255 / 5;
  return analog_value;
}

void Output::updateTickle()
{
  switch(output_number)
  {
    case 1:
      switch(tickle_div)
      {
        case 2:
          Fast_digitalWrite(25, LOW);
          Fast_digitalWrite(26, LOW);
          break;
        case 4:
          Fast_digitalWrite(25, HIGH);
          Fast_digitalWrite(26, LOW);
          break;
        case 8:
          Fast_digitalWrite(25, LOW);
          Fast_digitalWrite(26, HIGH);
          break;
        case 16:
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
          Fast_digitalWrite(28, LOW);
          Fast_digitalWrite(29, LOW);
          break;
        case 4:
          Fast_digitalWrite(28, HIGH);
          Fast_digitalWrite(29, LOW);
          break;
        case 8:
          Fast_digitalWrite(28, LOW);
          Fast_digitalWrite(29, HIGH);
          break;
        case 16:
          Fast_digitalWrite(28, HIGH);
          Fast_digitalWrite(29, HIGH);
          break;
        case 0:
          Fast_digitalWrite(34, HIGH);
          break;
      }
      Wire3.beginTransmission(MCP2);
      break;
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
  Wire3.write(wiper1);
  Wire3.write(amplitudeToAnalog(tickle_amplitude));
  Wire3.endTransmission(false);
}

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

void Output::chooseUpdateOutput()
{
  switch(output_number)
  {
    case 1:
      Fast_digitalWrite(9, HIGH);
      Fast_digitalWrite(9, LOW);
      break;
    case 2:
      Fast_digitalWrite(7, HIGH);
      Fast_digitalWrite(7, LOW);
      break;
    case 3:
      Fast_digitalWrite(5, HIGH);
      Fast_digitalWrite(5, LOW);
      break;
  }
}

void Output::resetFrequency()
{
  current_frequency = 1 / sqrt(1 / pow(start_frequency, 2) - period_squared_step);
}

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

void Output::updateFrequency(uint32_t del_phase)
{
  chooseSPIOutput();
  for(uint8_t i = 0; i < 32; i++)
  {
    Fast_digitalWrite(63, del_phase & 1)
    Fast_digitalWrite(62, HIGH);
    Fast_digitalWrite(62, LOW);
    del_phase >>= 1;
  }
  for(uint8_t i = 0; i < 8; i++)
  {
    Fast_digitalWrite(63, 0);
    Fast_digitalWrite(62, HIGH);
    Fast_digitalWrite(62, LOW);
  }
//  for(uint8_t i = 0; i < 4; i++)
//  {
//    SPI.transfer(del_phase & 0xFF);
//    del_phase>>=8;
//  }
//  SPI.transfer(0x00);
  chooseUpdateOutput();
}

void Output::run()
{
  updateFrequency(nextFrequency());
}

void Output::stop()
{
  updateFrequency(0);
}

// Scan function segment class
class Segment
{
  private:
    const static uint8_t num_outputs = 3;
    const static int DAC1 = 76;
    const static int DAC2 = 77;
    uint32_t duration;
    bool record;
    uint32_t num_freq_steps;
    const static uint8_t micros_per_step = 23;
    Output* output_list[num_outputs];
    uint8_t digital[12];
    double analog[8];
  public:
    Segment(JsonObject& segment);
    ~Segment();
    uint32_t getDuration();
    bool getRecord();
    void print();
    void setupSegment();
    void updateAnalogValue(uint8_t analog_output, double analog_volt);
    void updateAnalog();
    void run();
    void stop();
};

Segment::Segment(JsonObject& segment)
{
  duration = segment["Duration"];
  if(segment["Record"] == "True")
  {
    record = true;
  }
  else
  {
    record = false;
  }
  num_freq_steps = duration * 1000 / micros_per_step;
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    JsonObject& output_parameters = segment["Outputs"][i];
    output_list[i] = new Output(i, output_parameters, num_freq_steps);
  }
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
  for(uint8_t i = 0; i < segment["Analog"].size(); i++)
  {
    analog[i] = segment["Analog"][i];
    if(analog[i] != analog[i])
    {
      analog[i] = 0;
    }
  }
}

Segment::~Segment()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    delete output_list[i];
  }
}

uint32_t Segment::getDuration()
{
  return duration;
}

bool Segment::getRecord()
{
  return record;
}

void Segment::print()
{
  SerialASC.print("Duration: "); SerialASC.println(duration);
  SerialASC.print("Frequency steps: "); SerialASC.println(num_freq_steps);
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
    SerialASC.println("---------");
  }
}

void Segment::setupSegment()
{
  // Frequencies
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->resetFrequency();
  }
  // Analog
  for(uint8_t i = 0; i < 8; i++)
  {
    updateAnalogValue(i, analog[i]);
  }
  updateAnalog();
  // Duty cycles
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateDutyCycle();
  }
  // Tickle parameters
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->updateTickle();
  }
  // Digital
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
}

void Segment::updateAnalogValue(uint8_t analog_output, double analog_volt)
{
  if (analog_output < 4)
  {
    Wire2.beginTransmission(DAC1);
    Wire2.write((analog_output % 4) * 2);
    Wire2.write(highByte(voltToAnalog(analog_volt)));
    Wire2.write(lowByte(voltToAnalog(analog_volt)));
    Wire2.endTransmission(false);
  }
  else if (analog_output >= 4)
  {
    Wire2.beginTransmission(DAC2);
    Wire2.write((analog_output % 4) * 2);
    Wire2.write(highByte(voltToAnalog(analog_volt)));
    Wire2.write(lowByte(voltToAnalog(analog_volt)));
    Wire2.endTransmission(false);
  }
}

void Segment::updateAnalog()
{
  Wire2.beginTransmission(72);
  Wire2.write(48);
  Wire2.write(1);
  Wire2.write(1);
  Wire2.endTransmission(false);
}

uint16_t voltToAnalog(double volt)
{
  uint16_t analog_value = volt * 3281 + 33379;
  return analog_value;
}

void Segment::run()
{
  for(uint8_t i = 0; i < num_outputs; i++)
  {
    output_list[i]->run();
  }
}

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
    output_list[i]->stop();
  }
}

// Scan function class - container for the scan function segment objects
class ScanFunction
{
  private:
    uint8_t current_size;
    const static uint8_t max_size = 10;
    unsigned long previous_millis;
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

ScanFunction::ScanFunction()
{
  current_size = 0;
}

void ScanFunction::addSegment(JsonObject& segment)
{
  if(current_size < max_size)
  {
    segment_list[current_size] = new Segment(segment);
    current_size++;
  }
  else
  {
    SerialASC.println("Too many segments");
  }
}

uint32_t ScanFunction::getSegmentDuration(uint8_t segment_index)
{
  return segment_list[segment_index]->getDuration();
}

bool ScanFunction::getSegmentRecord(uint8_t segment_index)
{
  return segment_list[segment_index]->getRecord();
}

uint8_t ScanFunction::size()
{
  return current_size;
}

void ScanFunction::print()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    SerialASC.println("---------");
    SerialASC.print("Segment: "); SerialASC.println(i + 1);
    SerialASC.println("---------");
    segment_list[i]->print();
  }
}

void ScanFunction::clear()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    delete segment_list[i];
  }
  current_size = 0;
}

void ScanFunction::run()
{
  for(uint8_t i = 0; i < current_size; i++)
  {
    segment_list[i]->setupSegment();
    if(segment_list[i]->getRecord())
    {
//      data_acquire = true;
//      SerialASC.write(1);
      InterruptCore1();
//      Fast_digitalWrite(42, 1);
    }
    previous_millis = millis();
    while(millis() - previous_millis <= segment_list[i]->getDuration())
    {
      segment_list[i]->run();
    }
//    data_acquire = false;
//    if(segment_list[i]->getRecord())
//    {
//      Fast_digitalWrite(42, 0);
//      SerialASC.write(0);
//    }
  }
}

void ScanFunction::stop()
{
//  SerialASC.println("Stopping scan function");
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
uint32_t data_point_per_millis = 90;
uint32_t data_length_millis;


/*** Core 0 ***/

void setup() {
  // put your setup code for core 0 here, to run once:
  SerialASC.begin(SERIAL_RATE);
  SerialASC.setTimeout(SERIAL_TIMEOUT);
//  SPI.begin();
  pinMode(62, OUTPUT);
  pinMode(63, OUTPUT);
//  Wire.setWirePins(UsePins_16_17);
//  Wire.setWireBaudrate(400000);
  Wire3.begin();
  Wire3.setClock(152435);
//  Wire.beginTransmission(4);
//  Wire.endTransmission(false);
//  Wire.setClock(1000000);
  Wire2.begin();
  Wire2.setClock(155000);
  for(int i = 22; i < 54; i++)
  {
    pinMode(i, OUTPUT);
    digitalWrite(i, LOW);
  }
  for(int i = 4; i < 12; i++)
  {
    pinMode(i, OUTPUT);
  }
  Fast_digitalWrite(10, HIGH);
  Fast_digitalWrite(8, HIGH);
  Fast_digitalWrite(8, LOW);
  Fast_digitalWrite(9, HIGH);
  Fast_digitalWrite(9, LOW);
  Fast_digitalWrite(6, HIGH);
  Fast_digitalWrite(6, LOW);
  Fast_digitalWrite(7, HIGH);
  Fast_digitalWrite(7, LOW);
  Fast_digitalWrite(4, HIGH);
  Fast_digitalWrite(4, LOW);
  Fast_digitalWrite(5, HIGH);
  Fast_digitalWrite(5, LOW);
  CreateCore1Interrupt(StartDataAcquisition);
  
  SerialASC.println("Setup complete");
}


void loop()
{
  // put your main code for core 0 here, to run repeatedly:
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
//uint32_t data_length_points;
//uint16_t data;
//byte data_bytes[2];
//unsigned long start_time;
//bool start_signal;
//bool end_signal;
uint32_t record_duration;
EndOfUninitialised_CPU1_Variables

/* CPU1 Initialised Data */
StartOfInitialised_CPU1_Variables
/* Put your CPU1 fast access variables that have an initial value here e.g. uint32 CPU1_var_init = 1; */
//const byte end_byte[4] = {'s', 't', 'o', 'p'};
EndOfInitialised_CPU1_Variables

void setup1() {
  // put your setup code for core 1 here, to run once:
//  pinMode(A0, INPUT);
//  analogReadResolution(14);
//  Fast_digitalWrite(42, 1);
  pinMode(13, OUTPUT);
  digitalWrite(13, LOW);
}


void loop1() {
  // put your main code for core 1 here, to run repeatedly:
//  start_time = micros();
//  start_signal = true;
//  while(data_acquire)
//  {
//    if(start_signal)
//    {
//      SerialASC.println("$");
//      start_signal = false;
//    }
//    if(!end_signal)
//    {
//      end_signal = true;
//    }
//    data = ReadAD0();
//    SerialASC.write(highByte(data));
//    SerialASC.write(lowByte(data));
//  }
//  if(end_signal)
//  {
//    SerialASC.println("#");
////    SerialASC.write(end_byte, 4);
//    end_signal = false;
//  }
}

void StartDataAcquisition()
{
  uint32_t start_time = micros();
//  SerialASC.write(1);
  Fast_digitalWrite(13, 1);
  while(micros() - start_time < record_duration)
  {
  }
  Fast_digitalWrite(13, 0);
  SerialASC.write(0);
//  SerialASC.println('#');
//  SerialASC.println(data_length_points);
//  for(uint32_t i = 0; i < data_length_points; i++)
//  {
//    data = micros() - start_time;
//    SerialASC.write(highByte(data));
//    SerialASC.write(lowByte(data));
//  }
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
void downloadScan()
{
  SerialASC.println("Download initiated");
  scan_function.clear();
  StaticJsonBuffer<MAX_INPUT_LENGTH> json_buffer;
  JsonArray& scan_list = json_buffer.parseArray(SerialASC);
  if(scan_list.success())
  {
    data_length_millis = 0;
    for(uint8_t i = 0; i < scan_list.size(); i++)
    {
      JsonObject& segment = scan_list[i];
      scan_function.addSegment(segment);
      if(scan_function.getSegmentRecord(i))
      {
        record_duration = scan_function.getSegmentDuration(i) * 1000;
//        data_length_millis = scan_function.getSegmentDuration(i);
//        data_length_points = data_point_per_millis * data_length_millis;
      }
    }
    SerialASC.println("Download successful");
  }
  else
  {
    SerialASC.println("Download failed");
  }
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
//  SerialASC.println("Running scan function");
//  SerialASC.println(data_length_points);
  char choice = ' ';
  while(choice != 'S')
  {
//    InterruptCore1();
    scan_function.run();
    if(SerialASC.available())
    {
      choice = SerialASC.read();
    }
  }
  scan_function.stop();
  return;
}

void stopScan()
{
  scan_function.stop();
  return;
}
