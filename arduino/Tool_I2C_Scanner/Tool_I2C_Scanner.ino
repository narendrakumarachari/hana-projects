#include <Wire.h>

void setup() {
  Wire.begin();
  Serial.begin(9600);

  Serial.println("Scanning...");

  for (byte address = 1; address < 127; address++) {
    Wire.beginTransmission(address);

    if (Wire.endTransmission() == 0) {
      Serial.print("I2C device found at address: 0x");

      if (address < 16)
        Serial.print("0");

      Serial.println(address, HEX);
      delay(10);
    }
  }

  Serial.println("Scan Complete");
}

void loop() {
}