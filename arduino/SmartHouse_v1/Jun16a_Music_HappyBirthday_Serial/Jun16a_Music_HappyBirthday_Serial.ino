#define BUZZER 8

String command = "";

// Happy Birthday - corrected melody (25 notes)
int melody[] = {
  262, 262, 294, 262, 349, 330,        // Hap-py Birth-day to you
  262, 262, 294, 262, 392, 349,        // Hap-py Birth-day to you
  262, 262, 524, 440, 349, 330, 294,   // Hap-py Birth-day dear [name]
  466, 466, 440, 349, 392, 349         // Hap-py Birth-day to you
};

// Durations in ms — dotted quarter = 375, quarter = 250, half = 500, dotted half = 750
int noteDurations[] = {
  125, 375, 500, 500, 500, 750,
  125, 375, 500, 500, 500, 750,
  125, 375, 500, 500, 500, 500, 750,
  125, 375, 500, 500, 500, 750
};

void playHappyBirthday() {
  for (int i = 0; i < 25; i++) {
    tone(BUZZER, melody[i], noteDurations[i] * 0.9); // 10% gap between notes
    delay(noteDurations[i]);
  }
  noTone(BUZZER);
}

void setup() {
  Serial.begin(9600);
  Serial.println("Type: happy birthday");
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();
    command.toLowerCase();
    if (command == "happy birthday") {
      Serial.println("Playing Happy Birthday...");
      playHappyBirthday();
    }
  }
}