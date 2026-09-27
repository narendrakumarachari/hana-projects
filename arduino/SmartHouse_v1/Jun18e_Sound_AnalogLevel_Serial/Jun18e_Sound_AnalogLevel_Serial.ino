int soundPin = A0;

void setup() {
  Serial.begin(9600);
  Serial.println("Sound Sensor Reading Started");
}

void loop() {
  int soundValue = analogRead(soundPin);

  Serial.print("Sound Value: ");
  Serial.println(soundValue);

  delay(1000);  // Read once every 1 second
}