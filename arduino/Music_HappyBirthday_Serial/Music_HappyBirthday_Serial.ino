#define BUZZER 8

#define C4 262
#define D4 294
#define E4 330
#define F4 349
#define G4 392
#define A4 440
#define Bb4 466
#define C5 523

void playHappyBirthday() {
  int notes[] = {
    C4, C4, D4, C4, F4, E4,
    C4, C4, D4, C4, G4, F4,
    C4, C4, C5, A4, F4, E4, D4,
    Bb4, Bb4, A4, F4, G4, F4
  };

  int durations[] = {
    300, 150, 450, 450, 450, 900,
    300, 150, 450, 450, 450, 900,
    300, 150, 450, 450, 450, 450, 900,
    300, 150, 450, 450, 450, 900
  };

  for (int i = 0; i < 25; i++) {
    tone(BUZZER, notes[i]);
    delay(durations[i]);
    noTone(BUZZER);
    delay(50);
  }
}

void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();
    cmd.toLowerCase();

    if (cmd == "happy birthday") {
      playHappyBirthday();
    }
  }
}
