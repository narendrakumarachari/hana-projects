// ==========================================
// Natural Bird Chirping
// Passive Buzzer 1 -> Pin 2
// Passive Buzzer 2 -> Pin 3
// ==========================================

#define BUZZER1 2
#define BUZZER2 3

void setup() {
  pinMode(BUZZER1, OUTPUT);
  pinMode(BUZZER2, OUTPUT);

  randomSeed(analogRead(A0));   // Randomize chirps
}

void loop() {

  // Randomly choose one buzzer
  int buzzer = (random(2) == 0) ? BUZZER1 : BUZZER2;

  birdChirp(buzzer);

  // Natural pause between chirps
  delay(random(700, 3000));
}

void birdChirp(int pin) {

  // Random starting and ending frequencies
  int startFreq = random(1800, 2400);
  int endFreq   = random(3000, 3800);

  // Number of chirps in this call
  int chirps = random(1, 4);

  for (int c = 0; c < chirps; c++) {

    // Chirp Up
    for (int f = startFreq; f <= endFreq; f += random(25, 45)) {
      tone(pin, f);
      delay(random(2, 5));
    }

    // Chirp Down
    for (int f = endFreq; f >= startFreq; f -= random(25, 45)) {
      tone(pin, f);
      delay(random(2, 5));
    }

    noTone(pin);

    // Small gap between chirps
    delay(random(40, 150));
  }
}