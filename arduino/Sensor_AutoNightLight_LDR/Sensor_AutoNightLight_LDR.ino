int ldrPin = A0;
int ledPin = 11;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {

  int ldrValue = analogRead(ldrPin);

  Serial.print("LDR Value: ");
  Serial.println(ldrValue);

  if (ldrValue >= 650 && ldrValue < 850) {
    analogWrite(ledPin, 255);   // Full Brightness
  }
  else if (ldrValue >= 850 && ldrValue < 980) {
    analogWrite(ledPin, 128);   // Medium Brightness
  }
  else if (ldrValue >= 980) {
    analogWrite(ledPin, 0);     // OFF
  }

  delay(100);
}