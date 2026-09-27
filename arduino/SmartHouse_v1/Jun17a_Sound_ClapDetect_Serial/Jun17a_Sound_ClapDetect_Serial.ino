int soundPin = 12;

void setup() {
  pinMode(soundPin, INPUT);
  Serial.begin(9600);

  Serial.println("Sound Detection Started");
}

void loop() {
  int soundState = digitalRead(soundPin);

  if (soundState == HIGH) {   // Change to LOW if needed
    Serial.println("Clap Detected");
    delay(300);
  }
}