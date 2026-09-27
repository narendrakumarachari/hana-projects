#include <Servo.h>

Servo doorServo;

// Pin Definitions
const int servoPin = 10;
const int trigPin = 7;
const int echoPin = 6;
const int buzzerPin = 8;

// Door Settings
const int openAngle = 90;
const int closeAngle = 0;
const int detectDistance = 20;   // Detection distance in cm

bool doorBusy = false;

void setup() {
  Serial.begin(9600);

  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(buzzerPin, OUTPUT);

  digitalWrite(buzzerPin, LOW);

  doorServo.attach(servoPin);
  doorServo.write(closeAngle);

  Serial.println("===== Automatic Door System =====");
}

void loop() {

  long distance = getDistance();

  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (distance > 0 && distance <= detectDistance && !doorBusy) {

    doorBusy = true;

    Serial.println("Person Detected");
    Serial.println("Opening Door");

    // Beep 3 times
    for (int i = 0; i < 3; i++) {
      digitalWrite(buzzerPin, HIGH);
      delay(100);
      digitalWrite(buzzerPin, LOW);
      delay(100);
    }

    // Open Door Slowly
    for (int angle = closeAngle; angle <= openAngle; angle++) {
      doorServo.write(angle);
      delay(15);
    }

    Serial.println("Door Open");
    delay(5000);

    // Beep Once Before Closing
    digitalWrite(buzzerPin, HIGH);
    delay(300);
    digitalWrite(buzzerPin, LOW);

    Serial.println("Closing Door");

    // Close Door Slowly
    for (int angle = openAngle; angle >= closeAngle; angle--) {
      doorServo.write(angle);
      delay(15);
    }

    Serial.println("Door Closed");

    // Wait until person leaves
    while (true) {
      distance = getDistance();

      if (distance == -1 || distance > detectDistance) {
        break;
      }

      delay(100);
    }

    doorBusy = false;
  }

  delay(100);
}

//=========================
// Ultrasonic Distance
//=========================
long getDistance() {

  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);

  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);

  if (duration == 0)
    return -1;

  long distance = duration * 0.0343 / 2;

  return distance;
}