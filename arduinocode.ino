  /**
    * Hardware components on M3Bv2:
    * SerialM3B   - PinHeader                      - PA9, PA10, 9600baud 8N1
    * SerialMioty - mioty module                   - PC10, PC11, 9600baud 8N1
    * adxl362     - 3 axis accelerometer           - SPI, (CS-PA8, MISO-PA6, MOSI-PA7, SCLKPA5, INT1-PA11, INT2-PA12)
    * ms5637      - pressure sensor                - I2C Wire2(PB9, PB8)
    * sht31       - temperature & humidity sensor  - I2C Wire2(PB9, PB8)
    * si1141      - light sensor                   - I2C Wire2(PB9, PB8)
    * RGB LED     - low active                     - BLUE-PC6, LED-PC7, RED-PC8
    * Status LED  - high active                    - PC13
  */


// Libraries for Sensor use, MIOTY and M3 Board
#include <miotyAtClient.h>
#include "m3bDemoHelper.h"

#include "m3b_sensors/si1141.h"
#include <SHT31.h>
#include <SparkFun_MS5637_Arduino_Library.h>

//enable Serial Monitor
#include "SoftwareSerial.h"
// Debug Serial
SoftwareSerial SerialM3B(PA10, PA9);
// Mioty Bidi Stamp Serial
SoftwareSerial SerialMioty(PC11, PC10);

#include <SPI.h>
#include <SD.h>


//enable I2C
#include <Wire.h>

//Sensor Declaration
TwoWire Wire2(PB9, PB8);
MS5637 ms5637;
SHT31 sht31;
SI1141 si1141;

M3BDemoHelper m3bDemo;

// input new EUI
  uint8_t eui64[8] = {0x70, 0xb3, 0xd5, 0x67, 0x70, 0x11, 0x01, 0x81}; //change the last two byte according to the 'label' on your device
  uint8_t shortAdress[2] = {eui64[6], eui64[7]}; // get the last two byte as the short address

// input new Network Key
  uint8_t nwKey[16]={0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09,
          0x01, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f}; // This key must be same as the one set on loriot.

//Conditional compilation to set the network key once at the beginning,should be executed only ONCE and commented afterwards
#define SET_NETWORKKEY



File myFile;

uint16_t luminosityValue;



void setup() {
  // put your setup code here, to run once:
  m3bDemo.begin();
  SerialM3B.begin(9600);
  SerialMioty.begin(9600);

  //initialize sensors
  Wire2.begin();
  if (ms5637.begin(Wire2) == false)
  {
    SerialM3B.println("MS5637 sensor did not respond. Please check wiring.");
    while(1);
  }
  //sht31.begin(0x44, &Wire2);
  sht31.begin(0x44, &Wire2);
  si1141.begin(&Wire2);

  //Code for initial one-time setting of the network key, will only be executed if the constant SET_NETWORKKEY was defined previously

  #ifdef SET_NETWORKKEY
    // assign new EUI and Network Key
    uint8_t MSTA; // status of mac state machine

    // Local Dettach
    SerialM3B.print("Local Dettach:");
    miotyAtClient_macDetachLocal(&MSTA);

    // Set-EUI
    SerialM3B.print("Set EUI");
    miotyAtClient_getOrSetEui(eui64, true);
    miotyAtClient_getOrSetShortAdress(shortAdress, true);
    SerialM3B.println("");

    // Set-Network Key
    SerialM3B.print("Set Network Key");
    miotyAtClient_setNetworkKey(nwKey);
    SerialM3B.println("");

    // Local Attach - required only once
    SerialM3B.print("Local Attach:");
    miotyAtClient_macAttachLocal(&MSTA);
    SerialM3B.print("New Mac State:");
    SerialM3B.println(MSTA);
    SerialM3B.println("");
  #endif

  // get Device EUI
  uint8_t eui64[8];
  miotyAtClient_getOrSetEui( eui64, false);
  SerialM3B.print("Device EuI ");
  for (int i = 0; i < 8;i++) {
    SerialM3B.print(eui64[i], HEX);
    SerialM3B.print("-");
  }


  if (!SD.begin(PC9)) {
    SerialM3B.println("initialization failed!");
    while (1);
  }
  SerialM3B.println("initialization done.");

  
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(BLUE_LED, LOW);
  float temperature = sendWeatherData();
  digitalWrite(BLUE_LED, HIGH);

  delay(3000);

  // open the file. note that only one file can be open at a time,
  // so you have to close this one before opening another.
  myFile = SD.open("test.txt", FILE_WRITE);

  // if the file opened okay, write to it:
  if (myFile) {
    SerialM3B.print("Writing to test.txt...");

    // Write temperature, humidity, pressure, and illumination data to the file
    myFile.print("Temperature [°C]: ");
    myFile.println(temperature);
    myFile.print("Humidity [%]: ");
    myFile.println(sht31.getHumidity());
    myFile.print("Pressure [hPa]: ");
    myFile.println(ms5637.getPressure());
    
    si1141.readLuminosity(&luminosityValue);

    myFile.print("Luminosity: ");
    myFile.println(luminosityValue);

    // close the file:
    myFile.close();
    SerialM3B.println("done.");
  } else {
    // if the file didn't open, print an error:
    SerialM3B.println("error opening test.txt");
  }

}

float sendWeatherData() {
// readout of weather data; humidity in %, temperature in °C, pressure in hPa
  float pres=0., temp=0., hum=0.;
  temp = ms5637.getTemperature();
  pres = ms5637.getPressure();
  sht31.read();
  hum = sht31.getHumidity();
  uint16_t lux;
  si1141.readLuminosity(&lux);
  m3bDemo.transmitWeather(pres, temp, hum, lux);
 
  delay(4000);
  return temp;
}
