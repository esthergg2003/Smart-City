#include <miotyAtClient.h>
#include "m3bDemoHelper.h"

#include "m3b_sensors/si1141.h"
#include <SHT31.h>
#include <SparkFun_MS5637_Arduino_Library.h>

// Enable Serial Monitor
#include "SoftwareSerial.h"

// Debug Serial
SoftwareSerial SerialM3B(PA10, PA9);
// Mioty Bidi Stamp Serial
SoftwareSerial SerialMioty(PC11, PC10);

#include <SPI.h>
#include <SD.h>

// Enable I2C
#include <Wire.h>
#include <TimeLib.h>


// Sensor Declaration
TwoWire Wire2(PB9, PB8);
MS5637 ms5637;
SHT31 sht31;
SI1141 si1141;

M3BDemoHelper m3bDemo;

File myFile;
bool fileRead = false;

uint16_t luminosityValue;

void setup() {
  m3bDemo.begin();
  SerialM3B.begin(9600);
  SerialMioty.begin(9600);
  if (!SD.begin(PC9)) {
    //SerialM3B.println("Initialization failed!");
    while (1);
  }
  //SerialM3B.println("Initialization done.");

  // Check if the file has already been read
  if (!fileRead) {
    myFile = SD.open("test.txt");
    if (myFile) {
      //SerialM3B.println("test.txt:");
      // Read from the file until there's nothing else in it:
      while (myFile.available()) {
        SerialM3B.write(myFile.read());
      }
      // Close the file:
      myFile.close();
      fileRead = true; // Set the flag to indicate that the file has been read
    } else {
      // If the file didn't open, print an error:
      //SerialM3B.println("Error opening test.txt");
    }
  }
}

void loop() {
  //empty loop
}
