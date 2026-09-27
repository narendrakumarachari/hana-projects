
int ledPin = 11;
int numLoops = 5;  // Change this to the number of fade cycles

void setup() {
  pinMode(ledPin, OUTPUT);

  for (int loopCount = 0; loopCount < numLoops; loopCount++) {

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

  analogWrite(ledPin, 0); // Turn LED off after completing all loops
}

void loop() {
  // Nothing here
}