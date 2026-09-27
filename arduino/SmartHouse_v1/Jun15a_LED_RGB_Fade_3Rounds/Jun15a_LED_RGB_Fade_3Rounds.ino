int redPin = 9;
int greenPin = 10;
int bluePin = 11;

void setup() {
  pinMode(redPin, OUTPUT);
  pinMode(greenPin, OUTPUT);
  pinMode(bluePin, OUTPUT);
}

void fadeLED(int pin) {
  for (int i = 0; i <= 255; i++) {
    analogWrite(pin, i);
    delay(5);
  }

  for (int i = 255; i >= 0; i--) {
    analogWrite(pin, i);
    delay(5);
  }
}

void loop() {
  for (int count = 0; count <= 2; count++) {
    fadeLED(redPin);
    fadeLED(greenPin);
    fadeLED(bluePin);
  }
}