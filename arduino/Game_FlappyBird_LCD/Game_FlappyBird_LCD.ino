#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// ---- LCD config ----
LiquidCrystal_I2C lcd(0x27, 16, 2); // change to 0x3F if 0x27 doesn't work

// ---- Pins ----
#define PIN_VRY   A1
#define PIN_SW    3

// ---- Game constants ----
#define BIRD_COL      2
#define OBST_COUNT    3
#define SPACING       6
#define HOVER_TIME    250
#define MIN_TICK      140
#define START_TICK    320
#define FLAP_ANIM_MS  160   // how long wings stay "up" after a flap, for animation

// ---- Custom characters ----
// Bird flying level, wings up
byte birdWingUp[8] = {
  0b00000,
  0b00110,
  0b00010,
  0b01011,
  0b00000,
  0b00000,
  0b00000,
  0b00000
};
// Bird flying level, wings down (mid-flap)
byte birdWingDown[8] = {
  0b00000,
  0b00000,
  0b00000,
  0b01011,
  0b00010,
  0b00110,
  0b00000,
  0b00000
};
byte pipeBlock[8] = {
  0b11111,0b11111,0b11111,0b11111,0b11111,0b11111,0b11111,0b11111
};
byte deadBird[8] = {
  0b10001,0b01010,0b00100,0b01010,0b10001,0b00000,0b00000,0b00000
};

#define CH_BIRD_WUP   1
#define CH_BIRD_WDN   2
#define CH_PIPE       3
#define CH_DEAD       4

// ---- Game state ----
enum GameState { PLAYING, GAMEOVER };
GameState state = PLAYING;

struct Obstacle {
  int col;
  byte gapRow;
  bool scored;
};
Obstacle obst[OBST_COUNT];

byte birdRow = 1;
unsigned long lastFlap = 0;
unsigned long lastTick = 0;
unsigned long tickInterval = START_TICK;
int score = 0;
int highScore = 0;
bool wingUp = true;

// Frame buffers for dirty-cell diffing (prevents flicker)
char currFrame[2][16];
char prevFrame[2][16];

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);
  randomSeed(analogRead(A0));

  lcd.init();
  lcd.backlight();
  lcd.createChar(CH_BIRD_WUP, birdWingUp);
  lcd.createChar(CH_BIRD_WDN, birdWingDown);
  lcd.createChar(CH_PIPE, pipeBlock);
  lcd.createChar(CH_DEAD, deadBird);

  resetGame();
}

void resetGame() {
  birdRow = 1;
  lastFlap = millis();
  lastTick = millis();
  tickInterval = START_TICK;
  score = 0;
  wingUp = true;

  for (int i = 0; i < OBST_COUNT; i++) {
    obst[i].col = 15 + i * SPACING;
    obst[i].gapRow = random(0, 2);
    obst[i].scored = false;
  }

  for (int r = 0; r < 2; r++)
    for (int c = 0; c < 16; c++) {
      currFrame[r][c] = ' ';
      prevFrame[r][c] = '?'; // force full redraw first pass
    }

  state = PLAYING;
  lcd.clear();
  buildFrame();
  render();
}

void loop() {
  unsigned long now = millis();

  if (state == PLAYING) {
    readJoystick(now);

    // wing animation flaps quickly regardless of tick speed
    wingUp = ((now / FLAP_ANIM_MS) % 2 == 0);

    if (now - lastFlap > HOVER_TIME) {
      birdRow = 1; // gravity
    }

    // redraw bird position every short interval for smooth wing animation
    static unsigned long lastAnimDraw = 0;
    if (now - lastAnimDraw >= FLAP_ANIM_MS) {
      lastAnimDraw = now;
      buildFrame();
      render();
    }

    if (now - lastTick >= tickInterval) {
      lastTick = now;
      moveObstacles();
      if (checkCollision()) {
        gameOver();
      } else {
        buildFrame();
        render();
        if (tickInterval > MIN_TICK) tickInterval -= 2;
      }
    }
  } else { // GAMEOVER
    if (digitalRead(PIN_SW) == LOW) {
      delay(200);
      resetGame();
    }
  }
}

void readJoystick(unsigned long now) {
  int vy = analogRead(PIN_VRY);
  if (vy < 400) {
    birdRow = 0;
    lastFlap = now;
  }
}

void moveObstacles() {
  for (int i = 0; i < OBST_COUNT; i++) {
    obst[i].col--;

    if (obst[i].col == BIRD_COL && !obst[i].scored) {
      score++;
      obst[i].scored = true;
    }

    if (obst[i].col < -1) {
      obst[i].col += OBST_COUNT * SPACING;
      obst[i].gapRow = random(0, 2);
      obst[i].scored = false;
    }
  }
}

bool checkCollision() {
  for (int i = 0; i < OBST_COUNT; i++) {
    if (obst[i].col == BIRD_COL) {
      if (obst[i].gapRow != birdRow) return true;
    }
  }
  return false;
}

// Build the "should look like this" frame into currFrame
void buildFrame() {
  for (int r = 0; r < 2; r++)
    for (int c = 0; c < 16; c++)
      currFrame[r][c] = ' ';

  for (int i = 0; i < OBST_COUNT; i++) {
    int c = obst[i].col;
    if (c >= 0 && c < 16) {
      if (obst[i].gapRow == 0) currFrame[1][c] = CH_PIPE;
      else                     currFrame[0][c] = CH_PIPE;
    }
  }

  char birdChar = wingUp ? CH_BIRD_WUP : CH_BIRD_WDN;
  currFrame[birdRow][BIRD_COL] = birdChar;
}

// Only touch LCD cells that changed -> no flicker, no disappearing
void render() {
  for (int r = 0; r < 2; r++) {
    for (int c = 0; c < 16; c++) {
      if (currFrame[r][c] != prevFrame[r][c]) {
        lcd.setCursor(c, r);
        lcd.write((byte)currFrame[r][c]);
        prevFrame[r][c] = currFrame[r][c];
      }
    }
  }
}

void gameOver() {
  state = GAMEOVER;
  if (score > highScore) highScore = score;

  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.write((byte)CH_DEAD);
  lcd.print(" GAME OVER");
  lcd.setCursor(0, 1);
  lcd.print("Score:");
  lcd.print(score);
  lcd.print(" Hi:");
  lcd.print(highScore);
}