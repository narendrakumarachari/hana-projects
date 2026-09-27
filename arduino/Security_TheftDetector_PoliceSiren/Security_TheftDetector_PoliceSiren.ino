int ldrPin = A0;
int ledPin = 11;      // Street Light
int buzzerPin = 13;   // Passive Buzzer

int redPin = 4;       // RGB Red
int bluePin = 5;      // RGB Blue

#define TRIG_PIN 9
#define ECHO_PIN 10

void setup() {

  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  pinMode(redPin, OUTPUT);
  pinMode(bluePin, OUTPUT);

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  Serial.begin(9600);

  Serial.println("Smart Theft Detection System Started");
}

float getDistance() {

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);

  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH);

  float distance = duration * 0.0343 / 2;

  return distance;
}

void policeSiren() {

  // Rising Siren + Red LED

  for (int freq = 500; freq <= 1500; freq += 20) {

    tone(buzzerPin, freq);

    digitalWrite(redPin, HIGH);
    digitalWrite(bluePin, LOW);

    delay(5);
  }

  // Falling Siren + Blue LED

  for (int freq = 1500; freq >= 500; freq -= 20) {

    tone(buzzerPin, freq);

    digitalWrite(redPin, LOW);
    digitalWrite(bluePin, HIGH);

    delay(5);
  }

  noTone(buzzerPin);
}

void loop() {

  int ldrValue = analogRead(ldrPin);

  float distance = getDistance();

  Serial.print("LDR Value: ");
  Serial.print(ldrValue);

  Serial.print(" | Distance: ");
  Serial.print(distance);
  Serial.println(" cm");

  // NIGHT
  if (ldrValue >= 650 && ldrValue < 850) {

    analogWrite(ledPin, 255);

    Serial.println("Night Condition");

    if (distance > 3) {

      Serial.println("THEFT DETECTED!");

      policeSiren();
    }
    else {

      noTone(buzzerPin);

      digitalWrite(redPin, LOW);
      digitalWrite(bluePin, LOW);

      Serial.println("Object Present");
    }
  }

  // EVENING
  else if (ldrValue >= 850 && ldrValue < 980) {

    analogWrite(ledPin, 128);

    noTone(buzzerPin);

    digitalWrite(redPin, LOW);
    digitalWrite(bluePin, LOW);

    Serial.println("Evening Condition");
  }

  // DAY
  else if (ldrValue >= 980) {

    analogWrite(ledPin, 0);

    noTone(buzzerPin);

    digitalWrite(redPin, LOW);
    digitalWrite(bluePin, LOW);

    Serial.println("Day Condition");
  }

  // BELOW RANGE
  else {

    analogWrite(ledPin, 0);

    noTone(buzzerPin);

    digitalWrite(redPin, LOW);
    digitalWrite(bluePin, LOW);

    Serial.println("Below Threshold");
  }

  delay(3000);
}