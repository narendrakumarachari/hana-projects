int soundPin = 12;
int ledPin = 13;
int buzzerPin = 11;

void setup() {
  pinMode(soundPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(9600);
  Serial.println("Sound Detection Started");
}

void loop() {

  int soundState = digitalRead(soundPin);

  if (soundState == HIGH) {   // Change to LOW if your sensor is reversed

    Serial.println("Clap Detected");

    digitalWrite(ledPin, HIGH);
    digitalWrite(buzzerPin, HIGH);  // Active buzzer ON

  }
  else {

    digitalWrite(ledPin, LOW);
    digitalWrite(buzzerPin, LOW);   // Active buzzer OFF

  }

  delay(100);
}