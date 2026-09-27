#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <DHT.h>
#include <avr/pgmspace.h> // Required for PROGMEM (Flash Memory storage)

// ---------- LCD ----------
LiquidCrystal_I2C lcd(0x27, 16, 2);

// ---------- DHT ----------
#define DHTPIN A3
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ---------- Pins ----------
#define SERVO_PIN 2
#define TRIG_PIN 3
#define ECHO_PIN 4
#define ACTIVE_BUZZER 5 
#define RED_PIN 7
#define GREEN_PIN 8
#define BLUE_PIN 9
#define PASSIVE_BUZZER 10
#define LED_PIN 11
#define BUTTON_PIN 12
#define LDR_PIN A0

// ---------- Objects ----------
Servo doorServo; 

// ---------- Pitches Definitions ----------
#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1575
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951
#define NOTE_C8  4186
#define NOTE_CS8 4435
#define NOTE_D8  4699
#define NOTE_DS8 4967
#define REST      0

// ---------- Custom LCD Graphics ----------
// Updated Bird Character 
byte birdieGraphic[8] = {
  B00000,
  B11100, // Top wing going straight left
  B00100, // Body connection
  B10111, // Tail on the far left, beak on the right
  B00100, // Body connection
  B11100, // Bottom wing going straight left
  B00000,
  B00000
};


// Cloud character instead of Cactus
byte cloudGraphic[8] = {
  B00000,
  B00110,
  B01111,
  B11111,
  B11111,
  B00000,
  B00000,
  B00000
};

// ---------- Modes ----------
enum Mode {
  NORMAL,
  PARTY,
  BEDTIME,
  GAMEMODE
};

Mode currentMode = NORMAL;

// ---------- Variables ----------
long distanceCM = 100;
int songNumber = 0;
bool doorBusy = false;
bool serialLocked = false; 

unsigned long lastLCDUpdate = 0;
unsigned long lastFadeUpdate = 0;

int fadeValue = 0;
int fadeDirection = 1;

// Bedtime state tracking
bool bedtimeInitialized = false;
unsigned long bedtimeStartTime = 0;
bool bedtimeLocked = false;

// Game Mode tracking
bool gameInitialized = false;
bool isJumping = false;
unsigned long jumpStartTime = 0;
int cloudX = 15;
unsigned long lastGameUpdate = 0;
int playerScore = 0;

// Non-blocking music control variables
unsigned long lastNoteTime = 0;
int noteIndex = 0;
int currentSongPlaying = -1;
int durationOfNote = 0;
bool notePlaying = false;

// =====================================================================================
// ---------- FULL LENGTH MELODIES (STORED IN FLASH MEMORY VIA PROGMEM) ----------
// =====================================================================================

const int marioMelody[] PROGMEM = {
  NOTE_E5,8, NOTE_E5,8, REST,8, NOTE_E5,8, REST,8, NOTE_C5,8, NOTE_E5,8, 
  REST,8, NOTE_G5,8, REST,4, NOTE_G4,8, REST,4, 
  NOTE_C5,4, REST,8, NOTE_G4,8, REST,4, NOTE_E4,4, 
  REST,8, NOTE_A4,4, NOTE_B4,4, REST,8, NOTE_AS4,8, NOTE_A4,4,
  NOTE_G4,8, NOTE_E5,8, NOTE_G5,8, NOTE_A5,4, NOTE_F5,8, NOTE_G5,8, 
  REST,8, NOTE_E5,4, NOTE_C5,8, NOTE_D5,8, NOTE_B4,4,
  NOTE_C5,4, REST,8, NOTE_G4,8, REST,4, NOTE_E4,4, 
  REST,8, NOTE_A4,4, NOTE_B4,4, REST,8, NOTE_AS4,8, NOTE_A4,4,
  NOTE_G4,8, NOTE_E5,8, NOTE_G5,8, NOTE_A5,4, NOTE_F5,8, NOTE_G5,8, 
  REST,8, NOTE_E5,4, NOTE_C5,8, NOTE_D5,8, NOTE_B4,4
};
const int marioTempo = 180;
const int marioLength = sizeof(marioMelody) / sizeof(marioMelody[0]);

const int imperialMelody[] PROGMEM = {
  NOTE_A4,4, NOTE_A4,4, NOTE_A4,4, NOTE_F4,8, NOTE_C5,16, 
  NOTE_A4,4, NOTE_F4,8, NOTE_C5,16, NOTE_A4,2,
  NOTE_E5,4, NOTE_E5,4, NOTE_E5,4, NOTE_F5,8, NOTE_C5,16, 
  NOTE_GS4,4, NOTE_F4,8, NOTE_C5,16, NOTE_A4,2,
  NOTE_A5,4, NOTE_A4,8, NOTE_A4,16, NOTE_A5,4, NOTE_GS5,8, NOTE_G5,16, 
  NOTE_DS5,16, NOTE_D5,16, NOTE_DS5,8, REST,8, NOTE_A4,8, NOTE_DS5,4, NOTE_D5,8, NOTE_CS5,16,
  NOTE_C5,16, NOTE_B4,16, NOTE_C5,8, REST,8, NOTE_F4,8, NOTE_GS4,4, NOTE_F4,8, NOTE_A4,16, 
  NOTE_C5,4, NOTE_A4,8, NOTE_C5,16, NOTE_E5,2
};
const int imperialTempo = 120;
const int imperialLength = sizeof(imperialMelody) / sizeof(imperialMelody[0]);

const int odeMelody[] PROGMEM = {
  NOTE_E4,4, NOTE_E4,4, NOTE_F4,4, NOTE_G4,4, 
  NOTE_G4,4, NOTE_F4,4, NOTE_D4,4, NOTE_C4,4,
  NOTE_C4,4, NOTE_D4,4, NOTE_E4,4, NOTE_E4,4,
  NOTE_D4,2, NOTE_D4,2,
  NOTE_E4,4, NOTE_E4,4, NOTE_F4,4, NOTE_G4,4, 
  NOTE_G4,4, NOTE_F4,4, NOTE_D4,4, NOTE_C4,4,
  NOTE_C4,4, NOTE_D4,4, NOTE_E4,4, NOTE_D4,4,
  NOTE_C4,2, NOTE_C4,2,
  NOTE_D4,4, NOTE_D4,4, NOTE_E4,4, NOTE_C4,4, 
  NOTE_D4,4, NOTE_E4,8, NOTE_F4,8, NOTE_E4,4, NOTE_C4,4,
  NOTE_D4,4, NOTE_E4,8, NOTE_F4,8, NOTE_E4,4, NOTE_D4,4,
  NOTE_C4,4, NOTE_D4,4, NOTE_G3,2,
  NOTE_E4,4, NOTE_E4,4, NOTE_F4,4, NOTE_G4,4, 
  NOTE_G4,4, NOTE_F4,4, NOTE_D4,4, NOTE_C4,4,
  NOTE_C4,4, NOTE_D4,4, NOTE_E4,4, NOTE_D4,4,
  NOTE_C4,2, NOTE_C4,2
};
const int odeTempo = 120;
const int odeLength = sizeof(odeMelody) / sizeof(odeMelody[0]);

const int lullabyMelody[] PROGMEM = {
  NOTE_E4,4, NOTE_E4,4, NOTE_G4,2, NOTE_E4,4, NOTE_E4,4, NOTE_G4,2, 
  NOTE_E4,4, NOTE_G4,4, NOTE_C5,4, NOTE_B4,2, NOTE_A4,4, NOTE_A4,4, NOTE_G4,2,
  NOTE_D4,4, NOTE_E4,4, NOTE_F4,4, NOTE_D4,2, NOTE_D4,4, NOTE_E4,4, NOTE_F4,2, 
  NOTE_D4,4, NOTE_F4,4, NOTE_B4,4, NOTE_A4,4, NOTE_G4,2, NOTE_B4,4, NOTE_C5,2
};
const int lullabyTempo = 100;
const int lullabyLength = sizeof(lullabyMelody) / sizeof(lullabyMelody[0]);

// =====================================================================================

void setup() {
  Serial.begin(9600);

  pinMode(A4, INPUT_PULLUP);
  pinMode(A5, INPUT_PULLUP);

  lcd.init();
  lcd.backlight();
  
  // Register characters for Chrome Birdie Console
  lcd.createChar(0, birdieGraphic);
  lcd.createChar(1, cloudGraphic);

  dht.begin();

  doorServo.attach(SERVO_PIN);
  doorServo.write(0);   

  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  pinMode(ACTIVE_BUZZER, OUTPUT);
  pinMode(PASSIVE_BUZZER, OUTPUT);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);

  pinMode(LED_PIN, OUTPUT);

  pinMode(BUTTON_PIN, INPUT_PULLUP);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Smart House");
  lcd.setCursor(0,1);
  lcd.print("Normal Mode");

  Serial.println("Smart House Ready");
  Serial.println("Type help for commands");
}

void loop() {
  readSerial();
  distanceCM = getDistance();

  if(currentMode == NORMAL){
    noTone(PASSIVE_BUZZER); 
    normalMode();
  }
  else if(currentMode == PARTY){
    partyMode();
  }
  else if(currentMode == BEDTIME){
    bedtimeMode();
  }
  else if(currentMode == GAMEMODE){
    gameModeLoop();
  }
}

void normalMode() {
  bedtimeInitialized = false;
  bedtimeLocked = false;
  currentSongPlaying = -1; 

  float temp = dht.readTemperature();
  updateNightLight();

  if (millis() - lastLCDUpdate > 1000) {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Temp:");
    lcd.print(temp);
    lcd.print("C");

    lcd.setCursor(0,1);
    if (distanceCM <= 4) {
      lcd.print("Person:");
      lcd.print(distanceCM);
      lcd.print("cm");
    } else {
      lcd.print("No person");
    }
    lastLCDUpdate = millis();
  }

  if (distanceCM <= 4 && digitalRead(BUTTON_PIN) == LOW && !doorBusy) {
    if (!serialLocked) {
      openDoor();
    }
  }
}

void openDoor() {
  doorBusy = true;
  lcd.clear();
  lcd.print("Welcome");
  doorServo.write(90);
  delay(2500);   
  doorServo.write(0);
  lcd.clear();
  doorBusy = false;
}

long getDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  if(duration == 0){
    return 100;
  }
  long cm = duration * 0.034 / 2;
  return cm;
}

void updateNightLight() {
  int lightLevel = analogRead(LDR_PIN);

  if(lightLevel < 500) {
    if(millis() - lastFadeUpdate > 10) {
      fadeValue += fadeDirection;
      if(fadeValue >= 255){
        fadeValue = 255;
        fadeDirection = -1;
      }
      if(fadeValue <= 0){
        fadeValue = 0;
        fadeDirection = 1;
      }
      analogWrite(LED_PIN, fadeValue);
      lastFadeUpdate = millis();
    }
  } else {
    analogWrite(LED_PIN,0);
  }
}

void partyMode() {
  lcd.setCursor(0,0);
  lcd.print("PARTY'S ON      ");

  lcd.setCursor(0,1);
  if(songNumber == 0) lcd.print("Mario Theme     ");
  if(songNumber == 1) lcd.print("Imperial March  ");
  if(songNumber == 2) lcd.print("Ode to Joy      ");

  rainbowRGB();
  playSongBackground(songNumber);

  if(digitalRead(BUTTON_PIN) == LOW){
    delay(200); 
    songNumber++;
    if(songNumber > 2){
      songNumber = 0;
    }
    currentSongPlaying = -1; 
    lcd.clear();
  }
}

void rainbowRGB(){
  static unsigned long timer = 0;
  static int color = 0;

  if(millis() - timer > 200){
    timer = millis();
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);

    if(color == 0) digitalWrite(RED_PIN, HIGH);
    if(color == 1) digitalWrite(GREEN_PIN, HIGH);
    if(color == 2) digitalWrite(BLUE_PIN, HIGH);

    color++;
    if(color > 2) color = 0;
  }
}

void playSongBackground(int song) {
  int totalNotes = 0;
  int wholenote = 0;
  int tempo = 120;

  if(currentSongPlaying != song) {
    currentSongPlaying = song;
    noteIndex = 0;
    lastNoteTime = 0;
    notePlaying = false;
    noTone(PASSIVE_BUZZER);
  }

  if(song == 0) { totalNotes = marioLength; tempo = marioTempo; } 
  else if(song == 1) { totalNotes = imperialLength; tempo = imperialTempo; } 
  else if(song == 2) { totalNotes = odeLength; tempo = odeTempo; }
  else if(song == 3) { totalNotes = lullabyLength; tempo = lullabyTempo; }

  wholenote = (60000 * 4) / tempo;

  if (!notePlaying) {
    int pitch = 0;
    int durationVal = 0;

    if (song == 0) {
      pitch = pgm_read_word_near(marioMelody + noteIndex);
      durationVal = pgm_read_word_near(marioMelody + noteIndex + 1);
    } else if (song == 1) {
      pitch = pgm_read_word_near(imperialMelody + noteIndex);
      durationVal = pgm_read_word_near(imperialMelody + noteIndex + 1);
    } else if (song == 2) {
      pitch = pgm_read_word_near(odeMelody + noteIndex);
      durationVal = pgm_read_word_near(odeMelody + noteIndex + 1);
    } else if (song == 3) {
      pitch = pgm_read_word_near(lullabyMelody + noteIndex);
      durationVal = pgm_read_word_near(lullabyMelody + noteIndex + 1);
    }

    if (durationVal > 0) {
      durationOfNote = wholenote / durationVal;
    } else if (durationVal < 0) {
      durationOfNote = wholenote / abs(durationVal);
      durationOfNote *= 1.5; 
    }

    if (pitch != REST) {
      tone(PASSIVE_BUZZER, pitch, durationOfNote * 0.9);
    } else {
      noTone(PASSIVE_BUZZER);
    }

    lastNoteTime = millis();
    notePlaying = true;
  }

  if (notePlaying && (millis() - lastNoteTime >= durationOfNote)) {
    notePlaying = false;
    noteIndex += 2; 

    if (noteIndex >= totalNotes) {
      noteIndex = 0; 
    }
  }
}

void bedtimeMode(){
  if (!bedtimeInitialized) {
    analogWrite(LED_PIN, 0);
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);

    lcd.clear();
    lcd.print("Good night");
    
    currentSongPlaying = -1; 
    bedtimeStartTime = millis();
    bedtimeInitialized = true;
    bedtimeLocked = false;
  }

  if (bedtimeInitialized && !bedtimeLocked) {
    playSongBackground(3); 
    if (millis() - bedtimeStartTime >= 12000) { 
      lcd.clear();
      lcd.noBacklight(); 
      noTone(PASSIVE_BUZZER);
      bedtimeLocked = true;
    }
  }

  if (distanceCM <= 4) {
    intruderAlarm();
  }
}

// ---------- CHROME BIRDIE GAME MODE ----------
void gameModeLoop() {
  if (!gameInitialized) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Chrome Birdie");
    delay(1500);
    lcd.clear();
    cloudX = 15;
    playerScore = 0;
    isJumping = false;
    gameInitialized = true;
    lastGameUpdate = millis();
  }

  // Flap wings/Jump using the Servo motor button
  if (digitalRead(BUTTON_PIN) == LOW && !isJumping) {
    isJumping = true;
    jumpStartTime = millis();
    tone(PASSIVE_BUZZER, 400, 50); 
  }

  if (isJumping && (millis() - jumpStartTime > 700)) {
    isJumping = false;
  }

  // Refresh physics loop
  if (millis() - lastGameUpdate > 250) {
    lastGameUpdate = millis();
    cloudX--;

    if (cloudX < 0) {
      cloudX = 15;
      playerScore++;
      tone(PASSIVE_BUZZER, 900, 30); 
    }

    // Dynamic Cloud collision checking
    if (cloudX == 1 && !isJumping) {
      tone(PASSIVE_BUZZER, 150, 500); 
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("G_O! Score: ");
      lcd.print(playerScore);
      lcd.setCursor(0, 1);
      lcd.print("Restarting...");
      delay(3000);
      gameInitialized = false; 
      return;
    }

    lcd.clear();
    
    // Draw Birdie asset
    if (isJumping) {
      lcd.setCursor(1, 0);
    } else {
      lcd.setCursor(1, 1);
    }
    lcd.write(byte(0)); 

    // Draw Obstacle Cloud asset
    lcd.setCursor(cloudX, 1);
    lcd.write(byte(1));
    
    // Update live HUD
    lcd.setCursor(11, 0);
    lcd.print("S:");
    lcd.print(playerScore);
  }
}

void intruderAlarm(){
  lcd.backlight(); 
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("   INTRUDER!   ");

  while(getDistance() <= 6){
    digitalWrite(RED_PIN, HIGH);
    digitalWrite(BLUE_PIN, LOW);
    tone(PASSIVE_BUZZER, 800);
    delay(200);

    digitalWrite(RED_PIN, LOW);
    digitalWrite(BLUE_PIN, HIGH);
    tone(PASSIVE_BUZZER, 1200);
    delay(200);
  }

  noTone(PASSIVE_BUZZER);
  digitalWrite(RED_PIN, LOW);
  digitalWrite(BLUE_PIN, LOW);
  
  if (bedtimeLocked) {
    lcd.clear();
    lcd.noBacklight(); 
  } else {
    lcd.clear();
    lcd.print("Security Active");
  }
}

void readSerial(){
  if(!Serial.available()) return;

  String command = Serial.readStringUntil('\n');
  command.trim();
  command.toLowerCase();

  if(command == "help"){
    Serial.println("SMART HOUSE HELP");
    Serial.println("normal   - Switches house to standard mode");
    Serial.println("party    - Activates colorful lights and melodies");
    Serial.println("bedtime  - Begins the evening sleep lockdown routine");
    Serial.println("gamemode - Unlocks the mini Chrome Birdie LCD game console");
    Serial.println("lock     - Overrides and locks the entry servo motor");
    Serial.println("unlock   - Restores normal button/ultrasonic entry control");
    return;
  }

  if(command == "lock"){
    serialLocked = true;
    Serial.println("Door LOCKED. Servo button entry override active.");
    return;
  }

  if(command == "unlock"){
    serialLocked = false;
    Serial.println("Door UNLOCKED. Standard entry operational.");
    return;
  }

  if(command == "gamemode"){
    currentMode = GAMEMODE;
    gameInitialized = false; 
    lcd.backlight();
    Serial.println("Game Mode activated! Use the servo door button to fly over clouds.");
    return;
  }

  if(command == "normal"){
    digitalWrite(RED_PIN, LOW);
    digitalWrite(GREEN_PIN, LOW);
    digitalWrite(BLUE_PIN, LOW);

    if (currentMode == BEDTIME) {
      lcd.backlight();
      lcd.clear();
      lcd.print("Good morning.");

      int sunMelody[] = {NOTE_G4, NOTE_A4, NOTE_B4, NOTE_G4, NOTE_B4, NOTE_D5};
      int sunDurations[] = {4, 4, 2, 4, 4, 2};

      for (int i = 0; i < 6; i++) {
        digitalWrite(RED_PIN, HIGH);
        digitalWrite(GREEN_PIN, HIGH);
        digitalWrite(BLUE_PIN, LOW);

        int noteDuration = 1000 / sunDurations[i];
        tone(PASSIVE_BUZZER, sunMelody[i], noteDuration * 0.8);
        delay(noteDuration);

        digitalWrite(RED_PIN, LOW);
        digitalWrite(GREEN_PIN, LOW);
        delay(40);
      }
      noTone(PASSIVE_BUZZER);

      lastLCDUpdate = millis() + 2000; 
    }

    currentMode = NORMAL;
    lcd.backlight();
    lcd.clear();
    lcd.print("Normal Mode");
    Serial.println("System woken up to Normal Mode.");
  }

  if(command == "party"){
    currentMode = PARTY;
    lcd.backlight();
    lcd.clear();
    lcd.print("PARTY'S ON");
  }

  if(command == "bedtime"){
    currentMode = BEDTIME;
    bedtimeInitialized = false; 
  }
}