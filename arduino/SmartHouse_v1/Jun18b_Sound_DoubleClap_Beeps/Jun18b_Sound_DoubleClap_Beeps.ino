int soundPin = 12;
int ledPin = 13;
int buzzerPin = 11;

int clapCount = 0;
unsigned long firstClapTime = 0;

void setup() {
  pinMode(soundPin, INPUT);
  pinMode(ledPin, OUTPUT);
  pinMode(buzzerPin, OUTPUT);

  Serial.begin(9600);
}

void playTune() {
  digitalWrite(buzzerPin, HIGH);
  delay(200);
  digitalWrite(buzzerPin, LOW);
  delay(100);

  digitalWrite(buzzerPin, HIGH);
  delay(200);
  digitalWrite(buzzerPin, LOW);
  delay(100);

  digitalWrite(buzzerPin, HIGH);
  delay(500);
  digitalWrite(buzzerPin, LOW);
}

void loop() {

  if (digitalRead(soundPin) == HIGH) {

    clapCount++;

    Serial.print("Clap Count: ");
    Serial.println(clapCount);

    if (clapCount == 1) {
      firstClapTime = millis();

      digitalWrite(ledPin, HIGH);
      delay(500);
      digitalWrite(ledPin, LOW);
    }

    delay(300); // debounce
  }

  if (clapCount == 2 && (millis() - firstClapTime) < 1500) {

    Serial.println("Double Clap Detected!");
    playTune();

    clapCount = 0;
  }

  if (clapCount > 0 && (millis() - firstClapTime) > 1500) {
    clapCount = 0;
  }
}