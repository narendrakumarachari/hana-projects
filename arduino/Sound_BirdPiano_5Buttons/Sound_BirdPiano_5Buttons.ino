// ==========================================
// Krish's Bird Piano / Communication Board
// Sounds adapted to mimic House Sparrow vocalizations
// ==========================================
// Button 1 (Pin 2) - Meaning: Food (Rising Chirp)
// Button 2 (Pin 3) - Meaning: Water (Natural Randomized Chirp)
// Button 3 (Pin 4) - Meaning: Play (Natural Randomized Trill)
// Button 4 (Pin 5) - Meaning: Scritches (Natural Double Cheep)
// Button 5 (Pin 6) - Meaning: Outside (Complex Call)
// 
// Passive Buzzer: Pin 9

const int buttonPins[] = {2, 3, 4, 5, 6};
const int passiveBuzzerPin = 9;
const int numButtons = 5;

void setup() {
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP);
  }
  pinMode(passiveBuzzerPin, OUTPUT);
  
  // Seed the random generator using an unconnected analog pin for natural variations
  randomSeed(analogRead(A0)); 
}

// --- Sound 1: Original Rising Chirp (Kept as requested) ---
void chirpRising() {
  for (int freq = 2500; freq <= 4000; freq += 250) {
    tone(passiveBuzzerPin, freq, 20);
    delay(20);
  }
  noTone(passiveBuzzerPin);
}

// --- Sound 2: Natural Chirp ---
void naturalChirp() {
  int startFreq = random(1800, 2400);
  int endFreq   = random(3000, 3800);
  int chirps = random(1, 3); // Randomize 1 or 2 chirps per press

  for (int c = 0; c < chirps; c++) {
    // Chirp Up
    for (int f = startFreq; f <= endFreq; f += random(30, 50)) {
      tone(passiveBuzzerPin, f, 10);
      delay(random(2, 5));
    }
    // Chirp Down
    for (int f = endFreq; f >= startFreq; f -= random(30, 50)) {
      tone(passiveBuzzerPin, f, 10);
      delay(random(2, 5));
    }
    noTone(passiveBuzzerPin);
    
    // Natural pause between multi-chirps
    delay(random(40, 100)); 
  }
}

// --- Sound 3: Natural Trill ---
void naturalTrill() {
  int startFreq = random(3000, 3500);
  int endFreq   = random(4000, 4500);
  
  for (int c = 0; c < 5; c++) { // 5 rapid repetitions for a trill
    for (int f = startFreq; f <= endFreq; f += random(80, 120)) {
      tone(passiveBuzzerPin, f, 5);
      delay(2);
    }
    noTone(passiveBuzzerPin);
    delay(random(20, 40)); 
  }
}

// --- Sound 4: Natural Double Cheep (Fixed to remove robotic tone) ---
void naturalDoubleCheep() {
  for (int i = 0; i < 2; i++) { // Loop twice for a "double" cheep
    int startFreq = random(3800, 4200); // Start high
    int endFreq   = random(3200, 3600); // Slide down lower
    
    // Very fast downward slide to mimic a sharp, organic "peep"
    for (int f = startFreq; f >= endFreq; f -= random(80, 150)) {
      tone(passiveBuzzerPin, f, 5);
      delay(2);
    }
    noTone(passiveBuzzerPin);
    
    // Natural pause between the two cheeps
    delay(random(80, 120)); 
  }
}

// --- Sound 5: Complex Call (Fixed by using the new Natural Double Cheep) ---
void complexCall() {
  naturalDoubleCheep();
  delay(100);
  naturalChirp();
}

void loop() {
  // Check buttons and play corresponding sound
  if (digitalRead(buttonPins[0]) == LOW) {
    chirpRising();
    delay(800); // Prevent rapid re-triggering
  }
  
  if (digitalRead(buttonPins[1]) == LOW) {
    naturalChirp();
    delay(800);
  }
  
  if (digitalRead(buttonPins[2]) == LOW) {
    naturalTrill();
    delay(800);
  }
  
  if (digitalRead(buttonPins[3]) == LOW) {
    naturalDoubleCheep();
    delay(800);
  }
  
  if (digitalRead(buttonPins[4]) == LOW) {
    complexCall();
    delay(800);
  }

  // Small delay to stabilize button reads
  delay(10); 
}