// Push Button on Pin 13

const int buttonPin = 13;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);
}

void loop() {

  // Button pressed (LOW because of INPUT_PULLUP)
  if (digitalRead(buttonPin) == LOW) {
    Serial.println("Push Button is Pressed");
    delay(200);   // Prevents repeated messages too quickly
  }
}