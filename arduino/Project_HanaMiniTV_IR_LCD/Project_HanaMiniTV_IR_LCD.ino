#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <IRremote.hpp>

#define IR_RECEIVE_PIN 2
#define BUZZER_PIN     8

LiquidCrystal_I2C lcd(0x27, 16, 2);

bool tvOn = false;
bool isPaused = false;
int currentAnim = 0;          // 0 = welcome, 1-9 = channels
unsigned long lastFrameTime = 0;
int frameDelay = 150;         // Animation speed (ms)
int volumeLevel = 5;

// ============================================================================
// SYSTEM HELPERS & BEEP
// ============================================================================
void playBeep() {
  if (volumeLevel <= 0) return;
  int freq = 440 + (volumeLevel * 60);
  tone(BUZZER_PIN, freq, 50);
}

void showWelcome() {
  lcd.backlight();
  lcd.clear();
  lcd.setCursor(4, 0);
  lcd.print("Hana TV");
  lcd.setCursor(0, 1);
  lcd.print("Welcomes you!");
  playBeep();
  delay(1500);
  lcd.clear();
  lcd.setCursor(2, 0);
  lcd.print("Select Channel");
  lcd.setCursor(4, 1);
  lcd.print("1 to 9");
}

void showGoodbye() {
  lcd.clear();
  lcd.setCursor(3, 0);
  lcd.print("See you!");
  playBeep();
  delay(1500);
  lcd.clear();
  lcd.noBacklight();
}

void triggerEmergencyStop() {
  playBeep();
  lcd.clear();
  lcd.setCursor(1, 0);
  lcd.print("EMERGENCY STOP");
  delay(1000);
  lcd.clear();
  lcd.noBacklight();
  delay(5000);
  if (tvOn) {
    lcd.backlight();
    showWelcome();
  }
}

void changeVolume(int delta) {
  volumeLevel = constrain(volumeLevel + delta, 0, 10);
  playBeep();
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Volume: ");
  lcd.print(volumeLevel);
  lcd.print("/10");
  delay(600);
}

void togglePause() {
  isPaused = !isPaused;
  playBeep();
  lcd.clear();
  lcd.setCursor(4, 0);
  lcd.print(isPaused ? "PAUSED" : "RESUMED");
  delay(600);
}

// ============================================================================
// CHANNEL 1: GALLOPING HORSE
// ============================================================================
byte horseChr[2][8][8] = {
  {
    {0x00, 0x00, 0x00, 0x00, 0x03, 0x07, 0x0E, 0x0E},
    {0x00, 0x00, 0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F},
    {0x00, 0x00, 0x00, 0x03, 0x07, 0x1F, 0x1F, 0x1F},
    {0x00, 0x00, 0x05, 0x1F, 0x1D, 0x1F, 0x16, 0x06},
    {0x0C, 0x18, 0x10, 0x00, 0x01, 0x01, 0x01, 0x00},
    {0x1F, 0x1F, 0x1E, 0x17, 0x00, 0x00, 0x10, 0x00},
    {0x1F, 0x1F, 0x03, 0x02, 0x14, 0x04, 0x02, 0x00},
    {0x1C, 0x1C, 0x04, 0x04, 0x08, 0x00, 0x00, 0x00}
  },
  {
    {0x00, 0x00, 0x00, 0x07, 0x0F, 0x0E, 0x1C, 0x18},
    {0x00, 0x00, 0x00, 0x0F, 0x1F, 0x1F, 0x1F, 0x1F},
    {0x00, 0x00, 0x01, 0x03, 0x1F, 0x1F, 0x1F, 0x1F},
    {0x14, 0x1C, 0x1A, 0x1E, 0x1F, 0x13, 0x10, 0x10},
    {0x13, 0x13, 0x02, 0x02, 0x04, 0x00, 0x00, 0x00},
    {0x1F, 0x07, 0x0E, 0x06, 0x01, 0x00, 0x00, 0x00},
    {0x0F, 0x03, 0x03, 0x01, 0x01, 0x00, 0x00, 0x00},
    {0x10, 0x18, 0x0C, 0x02, 0x02, 0x11, 0x00, 0x00}
  }
};

int horseX = 0;
void runHorseFrame() {
  static int f = 0;
  lcd.clear();
  for (int i = 0; i < 8; i++) lcd.createChar(i, horseChr[f][i]);
  for (int c = 0; c < 4; c++) {
    int xc = horseX + c;
    if (xc >= 0 && xc < 16) {
      lcd.setCursor(xc, 0); lcd.write(byte(c));
      lcd.setCursor(xc, 1); lcd.write(byte(c + 4));
    }
  }
  f = (f + 1) % 2;
  horseX = (horseX + 1) % 16;
}

// ============================================================================
// CHANNEL 2: CHROME DINO GAME
// ============================================================================
byte dino_l[8] = { B00000111, B00000101, B00000111, B00010110, B00011111, B00011110, B00001110, B00000100 };
byte dino_r[8] = { B00000111, B00000101, B00000111, B00010110, B00011111, B00011110, B00001110, B00000010 };
byte cactus_s[8] = { 0b00100, 0b00101, 0b10101, 0b10101, 0b10111, 0b11100, 0b00100, 0b00000 };
byte cactus_b[8] = { B00000000, B00000100, B00000101, B00010101, B00010110, B00001100, B00000100, B00000100 };

char dinoWorld[32];
int dinoScore = 0;
int dinoJumpTimer = 0;
bool dinoInited = false;

void resetDinoGame() {
  dinoScore = 0;
  dinoJumpTimer = 0;
  const char header[] = "     Score:    0";
  for (int i = 0; i < 16; i++) dinoWorld[i] = header[i];
  dinoWorld[16] = 32; dinoWorld[17] = 0;
  for (int i = 18; i < 32; i++) dinoWorld[i] = 32;

  lcd.createChar(0, dino_l); lcd.createChar(1, dino_r);
  lcd.createChar(2, cactus_s); lcd.createChar(3, cactus_b);
}

void triggerDinoJump() {
  if (dinoJumpTimer == 0 && currentAnim == 2) {
    dinoJumpTimer = 4;
    if (volumeLevel > 0) tone(BUZZER_PIN, 1000, 80);
  }
}

void runDinoGameFrame() {
  if (!dinoInited) { resetDinoGame(); dinoInited = true; }
  if (dinoJumpTimer == 0 && (dinoWorld[18] == 2 || dinoWorld[18] == 3 || dinoWorld[19] == 2 || dinoWorld[19] == 3)) {
    triggerDinoJump();
  }
  if (dinoJumpTimer > 0) {
    dinoWorld[1] = 0; dinoWorld[17] = 32; dinoJumpTimer--;
  } else {
    dinoWorld[1] = 32; dinoWorld[17] = 0;
  }
  char random_object = random(2, 35);
  dinoWorld[31] = (random_object < 4) ? random_object : 32;

  bool gameOver = false;
  for (int i = 16; i < 32; i++) {
    if (dinoWorld[i] == 2 || dinoWorld[i] == 3) {
      char prev = (i < 31) ? dinoWorld[i + 1] : 32;
      if (dinoWorld[i - 1] < 2) gameOver = true;
      dinoWorld[i - 1] = dinoWorld[i]; dinoWorld[i] = prev;
    }
  }
  dinoWorld[15] = 32; if (dinoWorld[16] < 2) dinoWorld[16] = 32;

  if (gameOver) {
    if (volumeLevel > 0) tone(BUZZER_PIN, 300, 200);
    resetDinoGame(); return;
  }
  dinoScore++; if (dinoScore > 999) dinoScore = 0;
  lcd.setCursor(12, 0);
  if (dinoScore < 10) lcd.print("  "); else if (dinoScore < 100) lcd.print(" ");
  lcd.print(dinoScore);

  lcd.setCursor(0, 0);
  for (int i = 0; i < 32; i++) {
    if (dinoWorld[i] < 2) dinoWorld[i] ^= 1;
    if (i == 16) lcd.setCursor(0, 1);
    if (i < 12 || i > 15) lcd.write(byte(dinoWorld[i]));
  }
}

// ============================================================================
// CHANNEL 3: HUMAN HERO RUNNER ENGINE
// ============================================================================
#define HERO_RUN1 1
#define HERO_RUN2 2
#define HERO_JUMP 3
#define HERO_JUMP_LOWER 4
#define HERO_SOLID 5
#define HERO_SOLID_R 6
#define HERO_SOLID_L 7

static char terrainUpper[17];
static char terrainLower[17];
static byte heroPos = 1;
static byte newTerrainType = 0;
static byte newTerrainDuration = 1;
bool heroInited = false;

void initializeHeroGraphics() {
  static byte graphics[] = {
    B01100, B01100, B00000, B01110, B11100, B01100, B11010, B10011, // Run 1
    B01100, B01100, B00000, B01100, B01100, B01100, B01100, B01110, // Run 2
    B01100, B01100, B00000, B11110, B01101, B11111, B10000, B00000, // Jump upper
    B11110, B01101, B11111, B10000, B00000, B00000, B00000, B00000, // Jump lower
    B11111, B11111, B11111, B11111, B11111, B11111, B11111, B11111, // Solid ground
    B00011, B00011, B00011, B00011, B00011, B00011, B00011, B00011, // Solid R
    B11000, B11000, B11000, B11000, B11000, B11000, B11000, B11000, // Solid L
  };
  for (int i = 0; i < 7; ++i) lcd.createChar(i + 1, &graphics[i * 8]);
  for (int i = 0; i < 16; ++i) { terrainUpper[i] = ' '; terrainLower[i] = ' '; }
  heroPos = 1; newTerrainType = 0; newTerrainDuration = 10;
}

void triggerHeroJump() {
  if (currentAnim == 3 && heroPos <= 2) {
    heroPos = 3;
    if (volumeLevel > 0) tone(BUZZER_PIN, 800, 50);
  }
}

void advanceTerrain(char* terrain, byte newT) {
  for (int i = 0; i < 16; ++i) {
    char current = terrain[i];
    char next = (i == 15) ? newT : terrain[i + 1];
    if (current == ' ') terrain[i] = (next == HERO_SOLID) ? HERO_SOLID_R : ' ';
    else if (current == HERO_SOLID) terrain[i] = (next == ' ') ? HERO_SOLID_L : HERO_SOLID;
    else if (current == HERO_SOLID_R) terrain[i] = HERO_SOLID;
    else if (current == HERO_SOLID_L) terrain[i] = ' ';
  }
}

void runHeroRunnerFrame() {
  if (!heroInited) { initializeHeroGraphics(); heroInited = true; }

  advanceTerrain(terrainLower, newTerrainType == 1 ? HERO_SOLID : ' ');
  advanceTerrain(terrainUpper, newTerrainType == 2 ? HERO_SOLID : ' ');

  if (--newTerrainDuration == 0) {
    if (newTerrainType == 0) {
      newTerrainType = (random(3) == 0) ? 2 : 1;
      newTerrainDuration = 2 + random(8);
    } else {
      newTerrainType = 0; newTerrainDuration = 8 + random(8);
    }
  }

  if (heroPos <= 2 && terrainLower[3] != ' ') triggerHeroJump();

  char upperSave = terrainUpper[1];
  char lowerSave = terrainLower[1];
  byte u = ' ', l = ' ';

  if (heroPos == 1) l = HERO_RUN1;
  else if (heroPos == 2) l = HERO_RUN2;
  else if (heroPos == 3 || heroPos == 10) l = HERO_JUMP;
  else if (heroPos == 4 || heroPos == 9) { u = '.'; l = HERO_JUMP_LOWER; }
  else if (heroPos >= 5 && heroPos <= 8) u = HERO_JUMP;
  else if (heroPos == 11) u = HERO_RUN1;
  else if (heroPos == 12) u = HERO_RUN2;

  terrainUpper[1] = u; terrainLower[1] = l;
  terrainUpper[16] = '\0'; terrainLower[16] = '\0';

  lcd.setCursor(0, 0); lcd.print(terrainUpper);
  lcd.setCursor(0, 1); lcd.print(terrainLower);

  terrainUpper[1] = upperSave; terrainLower[1] = lowerSave;

  bool collide = (u != ' ' && upperSave != ' ') || (l != ' ' && lowerSave != ' ');
  if (collide) {
    for (int i = 0; i < 16; i++) { terrainUpper[i] = ' '; terrainLower[i] = ' '; }
    heroPos = 1; newTerrainType = 0; newTerrainDuration = 10;
  } else {
    if (heroPos == 2 || heroPos == 10) heroPos = 1;
    else if (heroPos >= 11) heroPos = (heroPos == 12) ? 11 : heroPos + 1;
    else ++heroPos;
  }
}

// ============================================================================
// CHANNEL 4: BUTTERFLY METAMORPHOSIS
// ============================================================================
byte eggIcon[8]       = { B00000, B00100, B01110, B01110, B00100, B00000, B11111, B00000 };
byte catPillar1[8]   = { B00000, B00000, B00000, B01010, B01110, B00100, B11111, B00000 };
byte catPillar2[8]   = { B00000, B00000, B00000, B00100, B01110, B01010, B11111, B00000 };
byte chrysalisIcon[8]= { B00100, B00100, B01110, B11111, B11111, B01110, B00100, B00000 };
byte bFlyUp[8]       = { B01010, B11111, B11111, B01110, B00100, B00100, B00000, B00000 };
byte bFlyDown[8]     = { B00000, B00000, B00100, B01110, B11111, B11111, B01010, B00000 };

int metaStage = 0;
int metaPos = 0;
int metaTimer = 0;

void runButterflyFrame() {
  lcd.clear();
  lcd.createChar(0, eggIcon);
  lcd.createChar(1, catPillar1);
  lcd.createChar(2, catPillar2);
  lcd.createChar(3, chrysalisIcon);
  lcd.createChar(4, bFlyUp);
  lcd.createChar(5, bFlyDown);

  metaTimer++;
  if (metaTimer > 20) {
    metaTimer = 0;
    metaStage = (metaStage + 1) % 4;
    metaPos = 0;
  }

  if (metaStage == 0) { // Egg on Leaf
    lcd.setCursor(0, 0); lcd.print("STAGE 1: EGG");
    lcd.setCursor(2, 1); lcd.write(byte(0));
    lcd.print("----------");
  } else if (metaStage == 1) { // Caterpillar Crawling
    lcd.setCursor(0, 0); lcd.print("STAGE 2: CATERP.");
    metaPos = (metaPos + 1) % 12;
    lcd.setCursor(metaPos, 1);
    lcd.write(byte((metaPos % 2 == 0) ? 1 : 2));
  } else if (metaStage == 2) { // Chrysalis
    lcd.setCursor(0, 0); lcd.print("STAGE 3: COCOON");
    lcd.setCursor(7, 0); lcd.write(byte(3));
    lcd.setCursor(0, 1); lcd.print("Transforming...");
  } else if (metaStage == 3) { // Flying Butterfly
    lcd.setCursor(0, 0); lcd.print("STAGE 4: BUTTERFLY");
    metaPos = (metaPos + 1) % 15;
    lcd.setCursor(metaPos, 1);
    lcd.write(byte((metaPos % 2 == 0) ? 4 : 5));
  }
}

// ============================================================================
// CHANNEL 5: WEATHER STATION
// ============================================================================
byte sunIcon[8]   = { B00100, B10101, B01110, B11111, B01110, B10101, B00100, B00000 };
byte cloudIcon[8] = { B00000, B00110, B01111, B11111, B11111, B00000, B00000, B00000 };
byte rainIcon[8]  = { B00110, B01111, B11111, B00000, B00100, B01000, B00100, B01000 };
byte stormIcon[8] = { B01111, B11111, B00100, B01000, B00100, B01000, B00100, B00000 };
byte snowIcon[8]  = { B01010, B00100, B10101, B00100, B01010, B00000, B10001, B00000 };

int weatherState = 0;
int weatherTimer = 0;

void runWeatherFrame() {
  lcd.clear();
  lcd.createChar(0, sunIcon);
  lcd.createChar(1, cloudIcon);
  lcd.createChar(2, rainIcon);
  lcd.createChar(3, stormIcon);
  lcd.createChar(4, snowIcon);

  weatherTimer++;
  if (weatherTimer > 15) {
    weatherTimer = 0;
    weatherState = (weatherState + 1) % 5;
  }

  lcd.setCursor(0, 0);
  if (weatherState == 0) {
    lcd.print("SUNNY DAY "); lcd.write(byte(0));
    lcd.setCursor(0, 1); lcd.print("Temp: 28C Sky: Clear");
  } else if (weatherState == 1) {
    lcd.print("CLOUDY "); lcd.write(byte(1));
    lcd.setCursor(0, 1); lcd.print("Temp: 22C Wind: 12m/s");
  } else if (weatherState == 2) {
    lcd.print("RAINING "); lcd.write(byte(2));
    lcd.setCursor(0, 1); lcd.print("Temp: 18C Rain: Heavy");
  } else if (weatherState == 3) {
    lcd.print("THUNDERSTORM "); lcd.write(byte(3));
    lcd.setCursor(0, 1); lcd.print("WARNING: Lightning!");
  } else if (weatherState == 4) {
    lcd.print("SNOWING "); lcd.write(byte(4));
    lcd.setCursor(0, 1); lcd.print("Temp: -4C Cold!");
  }
}

// ============================================================================
// CHANNELS 6-9: ADDITIONAL ANIMATIONS
// ============================================================================
byte heartIcon[8] = { B00000, B01010, B11111, B11111, B01110, B00100, B00000, B00000 };

void runHeartbeatFrame() {
  static bool big = false;
  lcd.clear();
  lcd.createChar(0, heartIcon);
  lcd.setCursor(0, 0); lcd.print("PULSE RATE: 72 BPM");
  lcd.setCursor(7, 1);
  if (big) lcd.write(byte(0)); else lcd.print(".");
  big = !big;
}

void runWaveFrame() {
  static int phase = 0;
  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("SINE WAVE MOTION");
  lcd.setCursor(0, 1);
  for (int i = 0; i < 16; i++) {
    int v = (i + phase) % 4;
    if (v == 0) lcd.print("-");
    else if (v == 1) lcd.print("^");
    else if (v == 2) lcd.print("-");
    else lcd.print("_");
  }
  phase = (phase + 1) % 4;
}

void runMatrixFrame() {
  lcd.clear();
  lcd.setCursor(0, 0);
  for (int i = 0; i < 16; i++) lcd.print((char)random(33, 126));
  lcd.setCursor(0, 1);
  for (int i = 0; i < 16; i++) lcd.print((char)random(33, 126));
}

void runShowcaseFrame() {
  static int subCh = 1;
  static int subTimer = 0;
  subTimer++;
  if (subTimer > 30) { subTimer = 0; subCh = (subCh % 5) + 1; }

  if (subCh == 1) runHorseFrame();
  else if (subCh == 2) runDinoGameFrame();
  else if (subCh == 3) runHeroRunnerFrame();
  else if (subCh == 4) runButterflyFrame();
  else if (subCh == 5) runWeatherFrame();
}

// ============================================================================
// TV SWITCHER & MAIN LOOP
// ============================================================================
String channelNames[10] = {
  "", "1: HORSE", "2: CHROME DINO", "3: HERO RUNNER",
  "4: BUTTERFLY", "5: WEATHER", "6: HEARTBEAT",
  "7: SINE WAVE", "8: MATRIX RAIN", "9: SHOWCASE DEMO"
};

void startAnimation(int n) {
  if (n < 1) n = 9;
  if (n > 9) n = 1;

  currentAnim = n;
  isPaused = false;
  dinoInited = false;
  heroInited = false;
  lastFrameTime = millis();
  playBeep();

  lcd.clear();
  lcd.setCursor(0, 0); lcd.print("TUNING TO...");
  lcd.setCursor(0, 1); lcd.print(channelNames[n]);
  delay(600);
}

void animationTick() {
  if (currentAnim == 0 || !tvOn || isPaused) return;
  if (millis() - lastFrameTime < frameDelay) return;
  lastFrameTime = millis();

  switch (currentAnim) {
    case 1: runHorseFrame(); break;
    case 2: runDinoGameFrame(); break;
    case 3: runHeroRunnerFrame(); break;
    case 4: runButterflyFrame(); break;
    case 5: runWeatherFrame(); break;
    case 6: runHeartbeatFrame(); break;
    case 7: runWaveFrame(); break;
    case 8: runMatrixFrame(); break;
    case 9: runShowcaseFrame(); break;
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(BUZZER_PIN, OUTPUT);
  lcd.init();
  lcd.noBacklight();
  randomSeed(analogRead(A0));
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
}

void loop() {
  animationTick();

  if (IrReceiver.decode()) {
    uint32_t code = IrReceiver.decodedIRData.decodedRawData;

    if (code == 0xBA45FF00) { // POWER
      tvOn = !tvOn;
      isPaused = false;
      if (tvOn) { currentAnim = 0; showWelcome(); }
      else { currentAnim = 0; showGoodbye(); }
      IrReceiver.resume();
      return;
    }

    if (!tvOn) { IrReceiver.resume(); return; }

    switch (code) {
      case 0xB946FF00: // VOL+ (Jump in Dino/Hero Runner)
        if (currentAnim == 2) triggerDinoJump();
        else if (currentAnim == 3) triggerHeroJump();
        else changeVolume(1); 
        break;

      case 0xEA15FF00: changeVolume(-1); break;                // VOL-
      case 0xB847FF00: triggerEmergencyStop(); break;          // FUNC/STOP
      case 0xBB44FF00: startAnimation(currentAnim - 1); break; // PREVIOUS
      case 0xBC39FF00:                                         // NEXT
      case 0xF20DFF00: startAnimation(currentAnim + 1); break; // REPEAT/NEXT
      case 0xBF40FF00:                                         // PLAY/PAUSE
        if (currentAnim == 2) triggerDinoJump();
        else if (currentAnim == 3) triggerHeroJump();
        else togglePause(); 
        break;

      // Channels 1-9
      case 0xF30CFF00: startAnimation(1); break; // 1 - HORSE
      case 0xE718FF00: startAnimation(2); break; // 2 - CHROME DINO
      case 0xA15EFF00: startAnimation(3); break; // 3 - HERO RUNNER
      case 0xF708FF00: startAnimation(4); break; // 4 - BUTTERFLY
      case 0xE31CFF00: startAnimation(5); break; // 5 - WEATHER
      case 0xA55AFF00: startAnimation(6); break; // 6 - HEARTBEAT
      case 0xBD42FF00: startAnimation(7); break; // 7 - SINE WAVE
      case 0xAD52FF00: startAnimation(8); break; // 8 - MATRIX RAIN
      case 0xB54AFF00: startAnimation(9); break; // 9 - SHOWCASE DEMO

      default:
        Serial.print("Unknown IR Code: 0x");
        Serial.println(code, HEX);
        break;
    }
    IrReceiver.resume();
  }
}