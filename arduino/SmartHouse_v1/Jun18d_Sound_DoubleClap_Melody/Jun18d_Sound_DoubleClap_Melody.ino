int soundPin = 12;
int ledPin = 13;
int buzzerPin = 11;

int clapCount = 0;
unsigned long firstClapTime = 0;

void playTune() {

  int melody[] = {
    262, 330, 392, 523,
    392, 330, 262
  };

  int duration[] = {
    200, 200, 200, 400,
    200, 200, 400
  };

  for (int i = 0; i < 7; i++) {
    tone(buzzerPin, melody[i]);
    delay(duration[i]);
    noTone(buzzerPin);
    delay(50);
  }
}

void setup() {
  pinMode(soundPin, INPUT);
  pinMode(ledPin, OUTPUT);

  Serial.begin(9600);
  Serial.println("Clap Detection Started");
}

void loop() {

  if (digitalRead(soundPin) == HIGH) {   // Change to LOW if needed

    clapCount++;

    Serial.print("Clap Count: ");
    Serial.println(clapCount);

    if (clapCount == 1) {

      firstClapTime = millis();

      digitalWrite(ledPin, HIGH);
      delay(300);
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
