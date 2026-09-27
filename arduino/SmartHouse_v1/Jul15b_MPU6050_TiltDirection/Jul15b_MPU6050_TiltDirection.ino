#include <Wire.h>

const int MPU = 0x68;

int16_t AcX, AcY, AcZ;

void setup() {
  Serial.begin(9600);

  Wire.begin();
  Wire.beginTransmission(MPU);
  Wire.write(0x6B);
  Wire.write(0);
  Wire.endTransmission(true);

  Serial.println("MPU6050 Ready");
}

void loop() {
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);
  Wire.endTransmission(false);
  Wire.requestFrom(MPU, 6, true);

  AcX = Wire.read() << 8 | Wire.read();
  AcY = Wire.read() << 8 | Wire.read();
  AcZ = Wire.read() << 8 | Wire.read();

  if (AcX > 6000)
    Serial.println("RIGHT");
  else if (AcX < -6000)
    Serial.println("LEFT");
  else if (AcY > 6000)
    Serial.println("UP");
  else if (AcY < -6000)
    Serial.println("DOWN");
  else
    Serial.println("CENTER");

  delay(2000);
}