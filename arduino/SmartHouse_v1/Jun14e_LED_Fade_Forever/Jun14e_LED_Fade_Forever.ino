int ledPin = 10;

void setup() {
  pinMode(ledPin, OUTPUT);
}

void loop() {
  // Fade In
  for (int brightness = 0; brightness <= 255; brightness++) {
    analogWrite(ledPin, brightness);
    delay(10);
  }

  // Fade Out
  for (int brightness = 255; brightness >= 0; brightness--) {
    analogWrite(ledPin, brightness);
    delay(10);
  }
}