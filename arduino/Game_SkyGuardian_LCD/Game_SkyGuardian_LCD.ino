#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2);

#define JOY_X A0
#define JOY_Y A1
#define JOY_BTN 3
#define BTN_LONG 8
#define BTN_SHORT 9
#define BUZZER 13

bool gameStarted = false;
int eggs = 5;
int score = 0;
int eagleX = 1;
int eagleY = 0;
bool poweredUp = false;
unsigned long powerUpEndTime = 0;

byte eagleSprite[8] = {
  B10001, B01010, B00100, B00100,
  B01010, B00000, B00000, B00000
};

struct SmallBug { int x; int y; bool active; };
SmallBug smallBugs[3];
struct BigBug { int x; int y; int hp; bool active; };
BigBug bigBugs[2];
struct Fish { int x; int y; bool active; };
Fish fishes[1];
struct Shot { int x; int y; bool active; bool isShortRange; int startX; int damage; };
Shot shots[5];

unsigned long lastEagleMove = 0;
unsigned long lastBugMove = 0;
unsigned long lastShotMove = 0;
unsigned long lastSpawn = 0;
bool lastLongState = HIGH;
bool lastShortState = HIGH;

void playShoot() { tone(BUZZER, 900, 30); }
void playHit() { tone(BUZZER, 500, 50); }
void playPowerUp() { tone(BUZZER, 1200, 150); }
void playWarn() { tone(BUZZER, 200, 200); }
void playOver() { tone(BUZZER, 150, 1000); }

void spawnEntities() {
  int r = random(0, 100);
  if (r < 10) { if (!fishes[0].active) { fishes[0].x = 15; fishes[0].y = random(0, 2); fishes[0].active = true; } }
  else if (r < 30) { for (int i = 0; i < 2; i++) { if (!bigBugs[i].active) { bigBugs[i].x = 15; bigBugs[i].y = random(0, 2); bigBugs[i].hp = 10; bigBugs[i].active = true; break; } } }
  else { for (int i = 0; i < 3; i++) { if (!smallBugs[i].active) { smallBugs[i].x = 15; smallBugs[i].y = random(0, 2); smallBugs[i].active = true; break; } } }
}

void fireShot(bool shortRange) {
  for (int i = 0; i < 5; i++) {
    if (!shots[i].active) {
      shots[i].x = eagleX + 1; shots[i].y = eagleY; shots[i].startX = eagleX + 1;
      shots[i].isShortRange = shortRange; shots[i].damage = shortRange ? 4 : 2; 
      shots[i].active = true; playShoot(); break;
    }
  }
}

void setup() {
  lcd.init(); lcd.backlight(); lcd.createChar(0, eagleSprite);
  pinMode(JOY_BTN, INPUT_PULLUP); pinMode(BTN_LONG, INPUT_PULLUP);
  pinMode(BTN_SHORT, INPUT_PULLUP); pinMode(BUZZER, OUTPUT);
  randomSeed(analogRead(A3));
}

void loop() {
  if (!gameStarted) {
    lcd.setCursor(2, 0); lcd.print("SKY GUARDIAN");
    lcd.setCursor(1, 1); lcd.print("PRESS JOYSTICK");
    if (digitalRead(JOY_BTN) == LOW) { delay(300); gameStarted = true; lcd.clear(); }
    return;
  }
  unsigned long currentMillis = millis();
  if (poweredUp && currentMillis > powerUpEndTime) poweredUp = false;
  int eagleSpeed = poweredUp ? 75 : 150;
  int shotSpeed = poweredUp ? 50 : 100;
  bool currentLongState = digitalRead(BTN_LONG);
  if (currentLongState == LOW && lastLongState == HIGH) fireShot(false);
  lastLongState = currentLongState;
  bool currentShortState = digitalRead(BTN_SHORT);
  if (currentShortState == LOW && lastShortState == HIGH) fireShot(true);
  lastShortState = currentShortState;
  if (currentMillis - lastEagleMove > eagleSpeed) {
    int xVal = analogRead(JOY_X); int yVal = analogRead(JOY_Y); bool moved = false;
    if (xVal < 300 && eagleX > 0) { eagleX--; moved = true; }
    if (xVal > 700 && eagleX < 15) { eagleX++; moved = true; }
    if (yVal < 300 && eagleY > 0) { eagleY--; moved = true; }
    if (yVal > 700 && eagleY < 1) { eagleY++; moved = true; }
    if (moved) lastEagleMove = currentMillis;
    if (fishes[0].active && eagleX == fishes[0].x && eagleY == fishes[0].y) { fishes[0].active = false; poweredUp = true; powerUpEndTime = currentMillis + 5000; playPowerUp(); }
  }
  if (currentMillis - lastShotMove > shotSpeed) {
    lastShotMove = currentMillis;
    for (int i = 0; i < 5; i++) {
      if (shots[i].active) {
        shots[i].x++;
        if (shots[i].isShortRange && (shots[i].x - shots[i].startX > 3)) shots[i].active = false;
        if (shots[i].x > 15) shots[i].active = false;
        if (shots[i].active) {
          for (int b = 0; b < 3; b++) { if (smallBugs[b].active && (shots[i].x == smallBugs[b].x || shots[i].x == smallBugs[b].x + 1) && shots[i].y == smallBugs[b].y) { smallBugs[b].active = false; shots[i].active = false; score += 1; playHit(); break; } }
          for (int b = 0; b < 2; b++) { if (shots[i].active && bigBugs[b].active && (shots[i].x == bigBugs[b].x || shots[i].x == bigBugs[b].x + 1) && shots[i].y == bigBugs[b].y) { bigBugs[b].hp -= shots[i].damage; shots[i].active = false; if (bigBugs[b].hp <= 0) { bigBugs[b].active = false; score += 2; playHit(); } break; } }
        }
      }
    }
  }
  if (currentMillis - lastBugMove > 600) {
    lastBugMove = currentMillis;
    for (int i = 0; i < 3; i++) { if (smallBugs[i].active) { smallBugs[i].x--; if (smallBugs[i].x < 0) { smallBugs[i].active = false; eggs--; playWarn(); } } }
    for (int i = 0; i < 2; i++) { if (bigBugs[i].active) { bigBugs[i].x--; if (bigBugs[i].x < 0) { bigBugs[i].active = false; eggs--; playWarn(); } } }
    if (fishes[0].active) { fishes[0].x--; if (fishes[0].x < 0) fishes[0].active = false; }
    if (eggs <= 0) {
      lcd.clear(); lcd.setCursor(3, 0); lcd.print("GAME OVER!"); lcd.setCursor(4, 1); lcd.print("SCORE: "); lcd.print(score); playOver();
      while(digitalRead(JOY_BTN) == HIGH) delay(50); delay(300); eggs = 5; score = 0; eagleX = 1; eagleY = 0; poweredUp = false; for(int b=0; b<3; b++) smallBugs[b].active = false; for(int b=0; b<2; b++) bigBugs[b].active = false; fishes[0].active = false; for(int s=0; s<5; s++) shots[s].active = false; lcd.clear(); gameStarted = false;
    }
  }
  if (currentMillis - lastSpawn > 2000) { lastSpawn = currentMillis; spawnEntities(); }
  lcd.clear(); lcd.setCursor(eagleX, eagleY); lcd.write(byte(0));
  for (int i = 0; i < 3; i++) { if (smallBugs[i].active && smallBugs[i].x >= 0 && smallBugs[i].x < 16) { lcd.setCursor(smallBugs[i].x, smallBugs[i].y); lcd.print("<"); } }
  for (int i = 0; i < 2; i++) { if (bigBugs[i].active && bigBugs[i].x >= 0 && bigBugs[i].x < 16) { lcd.setCursor(bigBugs[i].x, bigBugs[i].y); lcd.print("O"); } }
  if (fishes[0].active && fishes[0].x >= 0 && fishes[0].x < 16) { lcd.setCursor(fishes[0].x, fishes[0].y); lcd.print("*"); }
  for (int i = 0; i < 5; i++) { if (shots[i].active && shots[i].x >= 0 && shots[i].x < 16) { lcd.setCursor(shots[i].x, shots[i].y); lcd.print("-"); } }
  delay(30);
}