#include <Servo.h>

Servo doorServo;

const int servoPin = 10;
const int buttonPin = 9;

bool lastButtonState = HIGH;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);

  doorServo.attach(10);
  doorServo.write(0);   // Door Closed

  Serial.begin(9600);
  Serial.println("Door Ready");
}

void loop() {

  bool currentButtonState = digitalRead(buttonPin);

  // Button Press
  if (lastButtonState == HIGH && currentButtonState == LOW) {
    delay(30); // Debounce

    Serial.println("Door Opening...");

    // Open Door Slowly
    for (int angle = 0; angle <= 90; angle++) {
      doorServo.write(angle);
      delay(15);
    }

    Serial.println("Door Open");
    delay(5000);   // Keep door open for 5 seconds

    Serial.println("Door Closing...");

    // Close Door Slowly
    for (int angle = 90; angle >= 0; angle--) {
      doorServo.write(angle);
      delay(15);
    }

    Serial.println("Door Closed");
  }

  lastButtonState = currentButtonState;
}