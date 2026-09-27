#define SOUND_PIN 12
#define LED_PIN 13
#define BUZZER_PIN 8

int melody[] = {
  660,660,0,660,0,510,660,0,770,0,0,0,380,
  0,0,0,510,0,0,380,0,0,320,0,0,440,0,480,
  450,430,0,380,660,760,860,700,760,660,520,
  580,480
};

int noteCount = sizeof(melody) / sizeof(melody[0]);
int currentNote = 0;
unsigned long lastNoteTime = 0;
int noteDuration = 120;

void setup() {
  pinMode(SOUND_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  Serial.begin(9600);
  Serial.println("System Started");
}

void loop() {

  int soundState = digitalRead(SOUND_PIN);

  if (soundState == HIGH) {   // Change to LOW if your sensor works opposite

    digitalWrite(LED_PIN, HIGH);

    if (millis() - lastNoteTime >= noteDuration) {

      if (melody[currentNote] > 0) {
        tone(BUZZER_PIN, melody[currentNote]);
      } else {
        noTone(BUZZER_PIN);
      }

      currentNote++;
      if (currentNote >= noteCount) {
        currentNote = 0;
      }

      lastNoteTime = millis();
    }

    Serial.println("No Clap Detected");

  } else {

    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
    currentNote = 0;

    Serial.println("Clap Detected!");
    delay(300);
  }
}