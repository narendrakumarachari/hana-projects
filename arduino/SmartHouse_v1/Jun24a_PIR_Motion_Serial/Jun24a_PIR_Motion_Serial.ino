int pirPin = 5;

void setup() {
  pinMode(pirPin, INPUT);
  Serial.begin(9600);

  Serial.println("PIR Sensor Started");
}

void loop() {

  int motion = digitalRead(pirPin);

  if (motion == HIGH) {
    Serial.println("Motion Detected!");
    delay(1000); // Prevent repeated messages
  }
}