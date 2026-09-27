// LEDs on pins 4 to 13
const int leds[] = {4, 5, 6, 7, 8, 9, 10, 11, 12, 13};
const int numLeds = sizeof(leds) / sizeof(leds[0]);

const int buzzer = 3;

// Notes for buzzer
int notes[] = {
  262, 294, 330, 349, 392,
  440, 494, 523, 587, 659
};

void setup() {
  for (int i = 0; i < numLeds; i++) {
    pinMode(leds[i], OUTPUT);
    digitalWrite(leds[i], LOW);
  }

  pinMode(buzzer, OUTPUT);
}

void loop() {

  // Left to Right
  for (int i = 0; i < numLeds; i++) {
    showLED(i);
    tone(buzzer, notes[i], 70);
    delay(80);
  }

  // Right to Left
  for (int i = numLeds - 2; i > 0; i--) {
    showLED(i);
    tone(buzzer, notes[i], 70);
    delay(80);
  }
}

void showLED(int i) {
  clearAll();

  digitalWrite(leds[i], HIGH);

  if (i > 0)
    digitalWrite(leds[i - 1], HIGH);

  if (i < numLeds - 1)
    digitalWrite(leds[i + 1], HIGH);
}

void clearAll() {
  for (int i = 0; i < numLeds; i++) {
    digitalWrite(leds[i], LOW);
  }
}