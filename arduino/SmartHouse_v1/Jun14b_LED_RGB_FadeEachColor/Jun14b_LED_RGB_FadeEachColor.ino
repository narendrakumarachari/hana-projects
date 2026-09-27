int redPin = 9;
int greenPin = 10;
int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void fadeLED(int pin) {
  // Fade In
  for (int i = 0; i <= 255; i++) {
    analogWrite(pin, i);
    delay(5);
  }

  // Fade Out
  for (int i = 255; i >= 0; i--) {
    analogWrite(pin, i);
    delay(5);
  }
}

void loop() {
  fadeLED(redPin);    // Red fades
  fadeLED(greenPin);  // Green fades
  fadeLED(bluePin);   // Blue fades
}