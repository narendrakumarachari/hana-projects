int soundPin = A0;
int ledPin = 13;
int buzzerPin = 11;

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(9600);
  Serial.println("Sound Monitoring Started");
}

void loop() {

  int soundValue = analogRead(soundPin);

  Serial.print("Value: ");
  Serial.println(soundValue);

  if (soundValue >= 625) {

    digitalWrite(ledPin, HIGH);
    digitalWrite(buzzerPin, HIGH);

    delay(200);

    digitalWrite(ledPin, LOW);
    digitalWrite(buzzerPin, LOW);

    delay(200);
  }

  delay(1000);
}