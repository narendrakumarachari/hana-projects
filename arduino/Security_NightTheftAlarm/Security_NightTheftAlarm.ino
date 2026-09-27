int ldrPin = A0;
int ledPin = 11;
int buzzerPin = 13;

#define TRIG_PIN 9
#define ECHO_PIN 10

void setup() {
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.begin(9600);
}

void loop() {

  int ldrValue = analogRead(ldrPin);

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration * 0.0343 / 2;

  Serial.print("LDR: ");
  Serial.print(ldrValue);
  Serial.print("  Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  if (ldrValue >= 650 && ldrValue < 850) {

    analogWrite(ledPin, 255);

    if (distance > 5) {
      digitalWrite(buzzerPin, HIGH);
      Serial.println("Night - Object Missing - Alarm");
    }
    else {
      digitalWrite(buzzerPin, LOW);
      Serial.println("Night - Object Present");
    }
  }

  else if (ldrValue >= 850 && ldrValue < 980) {

    analogWrite(ledPin, 128);
    digitalWrite(buzzerPin, LOW);

    Serial.println("Evening Condition");
  }

  else if (ldrValue >= 980) {

    analogWrite(ledPin, 0);
    digitalWrite(buzzerPin, LOW);

    Serial.println("Day Condition");
  }

  delay(3000);
}