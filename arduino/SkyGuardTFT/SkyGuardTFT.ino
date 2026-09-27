// ======================================================================
//  SKY GUARD - TFT edition
//  ESP32 Dev Module + 1.54" 240x240 ST7789 (SPI) + joystick + 5 buttons
//  + passive buzzer
// ======================================================================
//
//  WIRING
//  TFT          ESP32            Joystick     ESP32
//   GND   ->    GND               GND   ->    GND
//   VCC   ->    3.3V              +5V   ->    3.3V  (NOT 5V!)
//   SCL   ->    GPIO 18           VRx   ->    GPIO 34  (left/right)
//   SDA   ->    GPIO 23           VRy   ->    GPIO 35  (up/down)
//   RST   ->    GPIO 4            SW    ->    GPIO 32  (talon flip)
//   DC    ->    GPIO 2
//   CS    ->    GPIO 5          Buttons (each: pin -> button -> GND)
//   BL    ->    3.3V              Button 1  short feather     GPIO 13
//                                 Button 2  long feather      GPIO 14
//  Passive buzzer                 Button 3  fire feather      GPIO 27
//   +     ->    GPIO 25           Button 4  electric feather  GPIO 26
//   -     ->    GND               Button 5  pause             GPIO 22
//
//  HOW TO PLAY
//   Joystick moves the eagle. Buttons 1-4 shoot the four feather types.
//   Click the joystick for a talon flip: it grabs any bug close by.
//   Button 5 pauses.
//   Don't let the bugs reach your nest on the left - they steal eggs!
// ======================================================================

#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>
#include <Preferences.h>
#include "GameTypes.h"
#include "Sprites.h"

// ---------------- Pins ----------------
#define TFT_CS   5
#define TFT_DC   2
#define TFT_RST  4

#define JOY_X    34
#define JOY_Y    35
#define JOY_SW   32

#define BTN1_SHORT  13
#define BTN2_LONG   14
#define BTN3_FIRE   27
#define BTN4_ZAP    26
#define BTN5_PAUSE  22

#define BUZZER   25

// Flip these if the joystick moves the eagle the wrong way
#define JOY_SWAP_XY   false
#define JOY_INVERT_X  false
#define JOY_INVERT_Y  false

// ---------------- Screen layout ----------------
#define SCR       240
#define HUD_H     22
#define GROUND_Y  214
#define STRIP_H   40      // screen is drawn in 6 strips of 240x40 (no flicker)
#define FRAME_MS  33      // ~30 fps

// ---------------- Game tuning ----------------
#define SHORT_RANGE     60        // short feathers fly 1/4 of the screen
#define SHORT_SPEED     7.0f
#define LONG_SPEED      3.5f      // long feathers are slower
#define SHORT_DAMAGE    4
#define LONG_DAMAGE     2
#define BIG_BUG_HP      10
#define FIRE_RECHARGE   25000
#define ZAP_RECHARGE    5000
#define ZAP_MAX_BUGS    5
#define PARALYZE_MS     3000
#define POWER_MS        5000
#define START_EGGS      5
#define STUNT_MS        500       // how long a talon flip lasts
#define STUNT_COOLDOWN  250       // extra wait before the next flip
#define TALON_RANGE     22        // how close a bug must be to get grabbed
#define TALON_DAMAGE    5         // damage to a big bug per flip

#define MAX_BUGS   8
#define MAX_BIG    3
#define MAX_SHOTS  10
#define MAX_PARTS  90
#define MAX_POPS   8

// ---------------- Colors ----------------
constexpr uint16_t rgb(uint8_t r, uint8_t g, uint8_t b) {
  return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
}
const uint16_t C_BLACK  = rgb(0, 0, 0);
const uint16_t C_WHITE  = rgb(255, 255, 255);
const uint16_t C_YELLOW = rgb(255, 220, 0);
const uint16_t C_GOLD   = rgb(255, 190, 40);
const uint16_t C_ORANGE = rgb(255, 120, 0);
const uint16_t C_RED    = rgb(230, 30, 30);
const uint16_t C_CYAN   = rgb(120, 230, 255);
const uint16_t C_GREEN  = rgb(60, 210, 60);
const uint16_t C_NAVY   = rgb(12, 22, 48);
const uint16_t C_GREY   = rgb(140, 160, 200);
const uint16_t C_CREAM  = rgb(255, 245, 215);

// ---------------- Hardware ----------------
Adafruit_ST7789 tft(TFT_CS, TFT_DC, TFT_RST);
GFXcanvas16 *cv;
int16_t oy = 0;           // top of the strip currently being drawn
Preferences prefs;

// ---------------- Sound ----------------
const Note S_SHORT[]  = {{1400, 20}, {1800, 20}};
const Note S_LONG[]   = {{600, 30}, {800, 30}, {1000, 30}};
const Note S_HIT[]    = {{400, 30}};
const Note S_KILL[]   = {{900, 25}, {1300, 35}};
const Note S_BIGKILL[] = {{300, 40}, {500, 40}, {800, 40}, {1200, 60}};
const Note S_FIRE[]   = {{180, 40}, {320, 40}, {150, 40}, {400, 40}, {120, 40}, {350, 40}, {100, 80}};
const Note S_ZAP[]    = {{2400, 20}, {1600, 20}, {2800, 20}, {1200, 20}, {3000, 20}, {2000, 40}};
const Note S_NOPE[]   = {{140, 80}};
const Note S_READY[]  = {{1568, 50}, {2093, 70}};
const Note S_POWER[]  = {{880, 60}, {1175, 60}, {1568, 120}};
const Note S_EGG[]    = {{220, 120}, {180, 160}};
const Note S_DROP[]   = {{500, 30}, {300, 40}};
const Note S_FLIP[]   = {{500, 30}, {750, 30}, {1100, 30}, {1500, 30}, {1100, 30}, {750, 30}};
const Note S_TALON[]  = {{1800, 20}, {900, 30}, {1400, 40}};
const Note S_PAUSE[]  = {{660, 60}, {880, 60}};
const Note S_START[]  = {{523, 100}, {659, 100}, {784, 100}, {1047, 220}};
const Note S_OVER[]   = {{523, 180}, {392, 180}, {330, 180}, {262, 500}};
#define PLAY(s) playSound(s, sizeof(s) / sizeof(Note))

const Note *sndSeq = nullptr;
uint8_t sndLen = 0, sndIdx = 0;
uint32_t sndNext = 0;

void playSound(const Note *s, uint8_t n) { sndSeq = s; sndLen = n; sndIdx = 0; sndNext = 0; }

void updateSound() {
  if (!sndSeq || millis() < sndNext) return;
  if (sndIdx >= sndLen) { noTone(BUZZER); sndSeq = nullptr; return; }
  Note n = sndSeq[sndIdx++];
  if (n.f) tone(BUZZER, n.f); else noTone(BUZZER);
  sndNext = millis() + n.ms;
}

// ---------------- Buttons ----------------
struct Button { uint8_t pin; bool stable, last; uint32_t changed; bool pressed; };
Button bJoy{JOY_SW, HIGH, HIGH, 0, false};
Button b1{BTN1_SHORT, HIGH, HIGH, 0, false};
Button b2{BTN2_LONG, HIGH, HIGH, 0, false};
Button b3{BTN3_FIRE, HIGH, HIGH, 0, false};
Button b4{BTN4_ZAP, HIGH, HIGH, 0, false};
Button b5{BTN5_PAUSE, HIGH, HIGH, 0, false};
Button *allBtns[] = {&bJoy, &b1, &b2, &b3, &b4, &b5};

void readButtons() {
  for (Button *b : allBtns) {
    bool r = digitalRead(b->pin);
    b->pressed = false;
    if (r != b->last) { b->last = r; b->changed = millis(); }
    if (millis() - b->changed > 25 && r != b->stable) {
      b->stable = r;
      if (r == LOW) b->pressed = true;
    }
  }
}

// ---------------- Joystick ----------------
int jcx = 2048, jcy = 2048;

float joyAxis(int raw, int c) {
  const int dz = 300;
  int d = raw - c;
  if (abs(d) < dz) return 0;
  float v = d > 0 ? float(d - dz) / max(1, 4095 - c - dz) : float(d + dz) / max(1, c - dz);
  return constrain(v, -1.0f, 1.0f);
}

void readJoystick(float &jx, float &jy) {
  float ax = joyAxis(analogRead(JOY_X), jcx);
  float ay = joyAxis(analogRead(JOY_Y), jcy);
  if (JOY_SWAP_XY) { float t = ax; ax = ay; ay = t; }
  if (JOY_INVERT_X) ax = -ax;
  if (JOY_INVERT_Y) ay = -ay;
  jx = ax; jy = ay;
}

// ---------------- Game objects ----------------
enum GameState { ST_TITLE, ST_PLAY, ST_PAUSE, ST_OVER };
GameState state = ST_TITLE;

Bug bugs[MAX_BUGS];
BigBug bigs[MAX_BIG];
Fish fish;
Feather shots[MAX_SHOTS];
Particle parts[MAX_PARTS];
Popup pops[MAX_POPS];
Cloud clouds[4];

float eagleX, eagleY;
int score = 0, best = 0, eggs = START_EGGS;
uint8_t boxFlash[4];       // HUD box lights up when that feather is shot
bool stunting = false;
uint32_t stuntStart, stuntReadyAt;
uint8_t stuntBigHit;       // big bugs already clawed during this flip (bitmask)
uint32_t gameMs, lastSpawn, fireReadyAt, zapReadyAt, powerEnd, overAt;
bool fireWasReady, zapWasReady, newBest;
float fireWaveX = -1;      // < 0 means no fire wave on screen
uint8_t zapCount = 0;
float zapTX[ZAP_MAX_BUGS], zapTY[ZAP_MAX_BUGS];
int16_t zapPts[ZAP_MAX_BUGS][7][2];
uint32_t zapShowEnd = 0;
uint8_t eggFlash = 0;
uint32_t animT = 0;
float scrollX = 0;
uint8_t hillFar[SCR], hillNear[SCR];
uint16_t skyCol[GROUND_Y];

// ---------------- Helpers ----------------
float randf(float a, float b) { return a + (b - a) * random(1000) / 1000.0f; }

uint32_t hash32(uint32_t n) {
  n ^= n >> 16; n *= 0x7feb352d; n ^= n >> 15; n *= 0x846ca68b; n ^= n >> 16;
  return n;
}

// Drawing wrappers: world coordinates -> current strip
inline bool visible(int top, int bottom) { return bottom >= oy && top < oy + STRIP_H; }
inline void fRect(int x, int y, int w, int h, uint16_t c) { cv->fillRect(x, y - oy, w, h, c); }
inline void fRound(int x, int y, int w, int h, int r, uint16_t c) { cv->fillRoundRect(x, y - oy, w, h, r, c); }
inline void dRound(int x, int y, int w, int h, int r, uint16_t c) { cv->drawRoundRect(x, y - oy, w, h, r, c); }
inline void fCirc(int x, int y, int r, uint16_t c) { cv->fillCircle(x, y - oy, r, c); }
inline void dCirc(int x, int y, int r, uint16_t c) { cv->drawCircle(x, y - oy, r, c); }
inline void fTri(int x0, int y0, int x1, int y1, int x2, int y2, uint16_t c) { cv->fillTriangle(x0, y0 - oy, x1, y1 - oy, x2, y2 - oy, c); }
inline void line(int x0, int y0, int x1, int y1, uint16_t c) { cv->drawLine(x0, y0 - oy, x1, y1 - oy, c); }
inline void px(int x, int y, uint16_t c) { cv->drawPixel(x, y - oy, c); }
inline void hLine(int x, int y, int w, uint16_t c) { cv->drawFastHLine(x, y - oy, w, c); }
inline void vLine(int x, int y, int h, uint16_t c) { cv->drawFastVLine(x, y - oy, h, c); }

void text(int x, int y, const char *s, uint8_t size, uint16_t c) {
  cv->setTextSize(size); cv->setTextColor(c); cv->setCursor(x, y - oy); cv->print(s);
}
void textC(int y, const char *s, uint8_t size, uint16_t c) {
  text((SCR - (int)strlen(s) * 6 * size) / 2, y, s, size, c);
}
void textShadowC(int y, const char *s, uint8_t size, uint16_t c) {
  int x = (SCR - (int)strlen(s) * 6 * size) / 2;
  text(x + 2, y + 2, s, size, C_NAVY);
  text(x, y, s, size, c);
}

// ---------------- Effects ----------------
void burst(float x, float y, uint8_t n, uint16_t c1, uint16_t c2, float spd) {
  for (uint8_t k = 0; k < n; k++) {
    for (Particle &p : parts) {
      if (p.life == 0) {
        float a = randf(0, 6.283f), v = randf(0.3f, 1.0f) * spd;
        p = {x, y, cosf(a) * v, sinf(a) * v, (k & 1) ? c1 : c2, (uint8_t)random(10, 22), (uint8_t)random(1, 3)};
        break;
      }
    }
  }
}

void addScore(int v, float x, float y) {
  score += v;
  for (Popup &p : pops) {
    if (p.life == 0) { p = {x, y, 24, (int8_t)v}; break; }
  }
}

void updateEffects() {
  for (Particle &p : parts) {
    if (!p.life) continue;
    p.x += p.vx; p.y += p.vy; p.vy += 0.06f; p.life--;
  }
  for (Popup &p : pops) {
    if (!p.life) continue;
    p.y -= 0.6f; p.life--;
  }
}

void updateScenery(float speed) {
  scrollX += speed;
  for (Cloud &c : clouds) {
    c.x -= c.spd * speed * 2;
    if (c.x < -30) { c.x = SCR + 30; c.y = randf(HUD_H + 15, 110); }
  }
  for (int x = 0; x < SCR; x++) {
    float fx = x + scrollX * 0.3f;
    hillFar[x] = 26 + 8 * sinf(fx * 0.025f) + 5 * sinf(fx * 0.061f + 1);
    float nx = x + scrollX * 0.7f;
    hillNear[x] = 12 + 6 * sinf(nx * 0.04f + 2) + 4 * sinf(nx * 0.09f);
  }
}

// ---------------- Game logic ----------------
void startGame() {
  for (Bug &b : bugs) b.st = B_DEAD;
  for (BigBug &g : bigs) g.active = false;
  for (Feather &f : shots) f.active = false;
  for (Particle &p : parts) p.life = 0;
  for (Popup &p : pops) p.life = 0;
  fish.active = false;
  eagleX = 40; eagleY = 110;
  score = 0; eggs = START_EGGS;
  stunting = false; stuntReadyAt = 0;
  memset(boxFlash, 0, sizeof(boxFlash));
  gameMs = 0; lastSpawn = 0; fireReadyAt = 0; zapReadyAt = 0; powerEnd = 0;
  fireWasReady = zapWasReady = true;
  fireWaveX = -1; zapShowEnd = 0; zapCount = 0; eggFlash = 0;
  state = ST_PLAY;
  PLAY(S_START);
}

void gameOver() {
  state = ST_OVER;
  overAt = millis();
  newBest = score > best;
  if (newBest) { best = score; prefs.putInt("best", best); }
  PLAY(S_OVER);
}

void stealEgg() {
  eggs--;
  eggFlash = 12;
  PLAY(S_EGG);
  burst(20, GROUND_Y - 10, 8, C_CREAM, C_RED, 2.0f);
  if (eggs <= 0) gameOver();
}

void spawnEntity() {
  int r = random(100);
  float y = randf(HUD_H + 14, GROUND_Y - 16);
  int level = min(score, 100);
  if (r < 10 && !fish.active) {
    fish = {250, y, y, true};
    return;
  }
  if (r < 30) {
    for (BigBug &g : bigs) {
      if (!g.active) { g = {252, y, 0.35f + level * 0.004f, BIG_BUG_HP, true, false, 0}; return; }
    }
  }
  for (Bug &b : bugs) {
    if (b.st == B_DEAD) { b = {250, y, y, 0, 0.7f + level * 0.012f, randf(0, 6.28f), B_ALIVE, false, 0}; return; }
  }
}

void killSmall(Bug &b, bool byFire) {
  if (byFire) burst(b.x, b.y, 12, C_ORANGE, C_YELLOW, 2.5f);
  else burst(b.x, b.y, 10, rgb(190, 90, 240), rgb(255, 150, 220), 2.0f);
  addScore(1, b.x, b.y - 8);
  b.st = B_DEAD; b.burning = false;
  PLAY(S_KILL);
}

void killBig(BigBug &g, bool byFire) {
  if (byFire) burst(g.x, g.y, 22, C_ORANGE, C_YELLOW, 3.0f);
  else burst(g.x, g.y, 22, C_RED, C_YELLOW, 3.0f);
  addScore(2, g.x, g.y - 14);
  g.active = false; g.burning = false;
  PLAY(S_BIGKILL);
}

bool useFire() {
  if (gameMs < fireReadyAt) { PLAY(S_NOPE); return false; }
  // Only bugs that are on screen right now get burned
  for (Bug &b : bugs)
    if (b.st != B_DEAD && b.x - 5 < SCR) b.burning = true;
  for (BigBug &g : bigs)
    if (g.active && g.x - 10 < SCR) g.burning = true;
  fireWaveX = 0;
  fireReadyAt = gameMs + FIRE_RECHARGE;
  fireWasReady = false;
  PLAY(S_FIRE);
  return true;
}

bool useZap() {
  if (gameMs < zapReadyAt) { PLAY(S_NOPE); return false; }
  uint8_t idx[MAX_BUGS]; float d[MAX_BUGS]; uint8_t n = 0;
  for (uint8_t i = 0; i < MAX_BUGS; i++) {
    Bug &b = bugs[i];
    if (b.st == B_ALIVE && !b.burning && b.x < SCR - 4) {
      float dx = b.x - eagleX, dy = b.y - eagleY;
      idx[n] = i; d[n] = dx * dx + dy * dy; n++;
    }
  }
  if (n == 0) { PLAY(S_NOPE); return false; }   // no small bugs: don't waste the charge

  // pick the closest bugs
  zapCount = min<uint8_t>(n, ZAP_MAX_BUGS);
  for (uint8_t a = 0; a < zapCount; a++) {
    uint8_t m = a;
    for (uint8_t k = a + 1; k < n; k++) if (d[k] < d[m]) m = k;
    float td = d[a]; d[a] = d[m]; d[m] = td;
    uint8_t ti = idx[a]; idx[a] = idx[m]; idx[m] = ti;
    Bug &b = bugs[idx[a]];
    b.st = B_PARALYZED;
    b.parEnd = gameMs + PARALYZE_MS;
    zapTX[a] = b.x; zapTY[a] = b.y;
  }
  zapShowEnd = gameMs + 400;
  zapReadyAt = gameMs + ZAP_RECHARGE;
  zapWasReady = false;
  PLAY(S_ZAP);
  return true;
}

// type: 0 short, 1 long, 2 fire, 3 electric
void shoot(uint8_t type) {
  if (type == 2) { if (useFire()) boxFlash[2] = 6; return; }
  if (type == 3) { if (useZap()) boxFlash[3] = 6; return; }
  for (Feather &f : shots) {
    if (!f.active) {
      bool isShort = type == 0;
      f = {eagleX + 20, eagleY - 2, eagleX + 20, isShort ? SHORT_SPEED : LONG_SPEED,
           (uint8_t)(isShort ? SHORT_DAMAGE : LONG_DAMAGE), isShort, true};
      burst(eagleX + 20, eagleY - 2, 3, C_WHITE, C_CYAN, 1.0f);
      if (isShort) PLAY(S_SHORT); else PLAY(S_LONG);
      boxFlash[type] = 6;
      return;
    }
  }
}

// ---- talon flip ----
void startStunt() {
  if (stunting || gameMs < stuntReadyAt) return;
  stunting = true;
  stuntStart = gameMs;
  stuntReadyAt = gameMs + STUNT_MS + STUNT_COOLDOWN;
  stuntBigHit = 0;
  PLAY(S_FLIP);
}

// Where the eagle is during the loop-the-loop and which way it faces.
// Upside down and backwards at the top of the loop.
void stuntPose(float &dx, float &dy, int8_t &flip) {
  dx = 0; dy = 0; flip = 1;
  if (!stunting) return;
  float a = (gameMs - stuntStart) * 6.283f / STUNT_MS;
  dx = sinf(a) * 14;
  dy = -(1 - cosf(a)) * 11;
  flip = cosf(a) >= 0 ? 1 : -1;
}

void updateStunt() {
  if (!stunting) return;
  if (gameMs - stuntStart >= STUNT_MS) { stunting = false; return; }
  float dx, dy; int8_t flip;
  stuntPose(dx, dy, flip);
  float ex = eagleX + dx, ey = eagleY + dy;
  burst(ex - 6, ey, 1, C_WHITE, C_CYAN, 0.3f);   // swoosh trail

  for (Bug &b : bugs) {
    if (b.st == B_DEAD) continue;
    float bx = b.x - ex, by = b.y - ey;
    if (bx * bx + by * by < TALON_RANGE * TALON_RANGE) {
      killSmall(b, false);
      burst(b.x, b.y, 6, C_YELLOW, C_WHITE, 2.0f);
      PLAY(S_TALON);
    }
  }
  for (uint8_t i = 0; i < MAX_BIG; i++) {
    BigBug &g = bigs[i];
    if (!g.active || (stuntBigHit & (1 << i))) continue;
    float bx = g.x - ex, by = g.y - ey;
    float r = TALON_RANGE + 6;
    if (bx * bx + by * by < r * r) {
      stuntBigHit |= 1 << i;
      g.hp -= TALON_DAMAGE;
      g.flash = 4;
      burst(g.x, g.y, 6, C_YELLOW, C_WHITE, 2.0f);
      if (g.hp <= 0) killBig(g, false); else PLAY(S_TALON);
    }
  }
}

void updateGame(uint32_t dt) {
  gameMs += dt;
  animT++;
  bool powered = gameMs < powerEnd;

  // ---- eagle ----
  float jx, jy;
  readJoystick(jx, jy);
  float spd = powered ? 5.0f : 3.2f;
  eagleX = constrain(eagleX + jx * spd, 22.0f, SCR - 22.0f);
  eagleY = constrain(eagleY + jy * spd, HUD_H + 16.0f, GROUND_Y - 18.0f);

  // ---- controls ----
  if (b1.pressed) shoot(0);
  if (b2.pressed) shoot(1);
  if (b3.pressed) shoot(2);
  if (b4.pressed) shoot(3);
  if (bJoy.pressed) startStunt();
  updateStunt();
  for (uint8_t &f : boxFlash) if (f) f--;

  // ---- recharge chimes ----
  bool fr = gameMs >= fireReadyAt, zr = gameMs >= zapReadyAt;
  if (fr && !fireWasReady) PLAY(S_READY);
  else if (zr && !zapWasReady) PLAY(S_READY);
  fireWasReady = fr; zapWasReady = zr;

  // ---- spawning (gets faster as score goes up) ----
  uint32_t interval = max(650, 1800 - score * 12);
  if (gameMs - lastSpawn > interval) { lastSpawn = gameMs; spawnEntity(); }

  // ---- feathers ----
  float mult = powered ? 1.6f : 1.0f;
  for (Feather &f : shots) {
    if (!f.active) continue;
    f.x += f.speed * mult;
    if (f.isShort && f.x - f.startX > SHORT_RANGE) {
      f.active = false;
      burst(f.x, f.y, 3, C_WHITE, C_GREY, 0.8f);
      continue;
    }
    if (f.x > SCR + 10) { f.active = false; continue; }

    for (Bug &b : bugs) {
      if (b.st != B_ALIVE && b.st != B_PARALYZED) continue;
      float dx = f.x - b.x, dy = f.y - b.y;
      if (dx * dx + dy * dy < 110) { killSmall(b, false); f.active = false; break; }
    }
    if (!f.active) continue;
    for (BigBug &g : bigs) {
      if (!g.active) continue;
      if (fabsf(f.x - g.x) < 17 && fabsf(f.y - g.y) < 12) {
        f.active = false;
        g.hp -= f.dmg;
        g.flash = 4;
        burst(f.x, f.y, 4, C_WHITE, C_YELLOW, 1.2f);
        if (g.hp <= 0) killBig(g, false); else PLAY(S_HIT);
        break;
      }
    }
  }

  // ---- small bugs ----
  for (Bug &b : bugs) {
    switch (b.st) {
      case B_ALIVE:
        b.x -= b.speed;
        b.phase += 0.12f;
        b.y = b.baseY + sinf(b.phase) * 6;
        if (b.x < -8) { b.st = B_DEAD; b.burning = false; stealEgg(); }
        break;
      case B_PARALYZED:
        if (gameMs >= b.parEnd) { b.st = B_FALLING; b.vy = 0.5f; }
        break;
      case B_FALLING:
        b.vy += 0.35f;
        b.y += b.vy;
        if (b.y >= GROUND_Y - 4) {
          burst(b.x, GROUND_Y - 2, 8, rgb(150, 110, 70), rgb(200, 170, 120), 1.5f);
          addScore(1, b.x, GROUND_Y - 16);
          b.st = B_DEAD; b.burning = false;
          PLAY(S_DROP);
        }
        break;
      default: break;
    }
  }

  // ---- big bugs ----
  for (BigBug &g : bigs) {
    if (!g.active) continue;
    g.x -= g.speed;
    if (g.flash) g.flash--;
    if (g.x < -12) { g.active = false; g.burning = false; stealEgg(); }
  }

  // ---- fish power-up ----
  if (fish.active) {
    fish.x -= 1.3f;
    fish.y = fish.baseY + sinf(animT * 0.15f) * 4;
    float dx = fish.x - eagleX, dy = fish.y - eagleY;
    if (dx * dx + dy * dy < 500) {
      fish.active = false;
      powerEnd = gameMs + POWER_MS;
      burst(fish.x, fish.y, 16, C_GOLD, C_YELLOW, 2.5f);
      PLAY(S_POWER);
    } else if (fish.x < -12) fish.active = false;
  }

  // ---- fire wave ----
  if (fireWaveX >= 0) {
    fireWaveX += 14;
    for (Bug &b : bugs)
      if (b.st != B_DEAD && b.burning && b.x <= fireWaveX) killSmall(b, true);
    for (BigBug &g : bigs)
      if (g.active && g.burning && g.x <= fireWaveX) killBig(g, true);
    if (fireWaveX > SCR + 20) {
      fireWaveX = -1;
      for (Bug &b : bugs) if (b.st != B_DEAD && b.burning) killSmall(b, true);
      for (BigBug &g : bigs) if (g.active && g.burning) killBig(g, true);
    }
  }

  // ---- electric bolts (jagged, redrawn every frame) ----
  if (gameMs < zapShowEnd) {
    for (uint8_t k = 0; k < zapCount; k++) {
      float x0 = eagleX + 20, y0 = eagleY - 2, x1 = zapTX[k], y1 = zapTY[k];
      for (uint8_t s = 0; s <= 6; s++) {
        float t = s / 6.0f;
        int j = (s > 0 && s < 6) ? 7 : 0;
        zapPts[k][s][0] = x0 + (x1 - x0) * t + (j ? random(-j, j + 1) : 0);
        zapPts[k][s][1] = y0 + (y1 - y0) * t + (j ? random(-j, j + 1) : 0);
      }
    }
  }

  if (eggFlash) eggFlash--;
  updateEffects();
  updateScenery(0.6f);
}

// ---------------- Drawing: sprites ----------------
// Sprites are pixel art from Sprites.h, drawn at 2x size.
#define SPR_SCALE 2
enum Tint : uint8_t { TINT_NONE, TINT_ZAP, TINT_FIRE, TINT_FLASH, TINT_COUNT };
uint16_t spritePal[TINT_COUNT][128];

uint16_t spriteColor(char ch) {
  switch (ch) {
    case 'K': return rgb(30, 20, 15);     // outline
    case 'B': return rgb(125, 70, 30);    // brown
    case 'D': return rgb(85, 45, 18);     // dark brown
    case 'L': return rgb(175, 115, 60);   // light brown
    case 'W': return rgb(250, 250, 245);  // white
    case 'G': return rgb(185, 190, 205);  // white shade
    case 'Y': return rgb(255, 205, 0);    // yellow
    case 'O': return rgb(220, 130, 0);    // dark yellow
    case 'E': return rgb(0, 0, 0);        // eye
    case 'P': return rgb(150, 60, 200);   // purple
    case 'Q': return rgb(90, 30, 130);    // dark purple
    case 'M': return rgb(205, 130, 240);  // light purple
    case 'S': return rgb(250, 210, 40);   // stripe
    case 'R': return rgb(215, 40, 40);    // red
    case 'r': return rgb(140, 20, 20);    // dark red
    case 'N': return rgb(35, 25, 25);     // near black
    case 'C': return rgb(215, 240, 255);  // wing light
    case 'c': return rgb(150, 195, 235);  // wing mid
    case 'F': return rgb(255, 150, 20);   // fish orange
    case 'f': return rgb(215, 85, 0);     // fish dark
    case 'H': return rgb(255, 225, 160);  // highlight
    case 'w': return rgb(255, 255, 255);  // shine
    default:  return rgb(255, 0, 255);
  }
}

// Builds the normal palette plus tinted versions for paralyzed (blue),
// burning (orange) and hit-flash (white). Outlines stay dark.
void buildPalettes() {
  const char *letters = "KBDLWGYOEPQMSRrNCcFfHw";
  for (const char *p = letters; *p; p++) {
    uint16_t c = spriteColor(*p);
    uint8_t r = (c >> 11) << 3, g = ((c >> 5) & 0x3F) << 2, b = (c & 0x1F) << 3;
    int lum = (r * 3 + g * 6 + b) / 10;
    bool keep = *p == 'K' || *p == 'E' || *p == 'N';
    spritePal[TINT_NONE][(uint8_t)*p] = c;
    spritePal[TINT_ZAP][(uint8_t)*p] = keep ? c : rgb(lum / 3, min(255, lum * 3 / 4 + 70), min(255, lum + 130));
    spritePal[TINT_FIRE][(uint8_t)*p] = keep ? c : rgb(min(255, lum + 140), lum * 3 / 5, 0);
    spritePal[TINT_FLASH][(uint8_t)*p] = keep ? c : C_WHITE;
  }
}

// (x, y) is the sprite's top-left corner. flip = -1 turns it upside down and backwards.
void drawSprite(const char *const *rows, int w, int h, int x, int y, int8_t flip, uint8_t tint) {
  const int s = SPR_SCALE;
  if (!visible(y, y + h * s)) return;
  const uint16_t *pal = spritePal[tint];
  int r0 = max(0, (oy - y) / s), r1 = min(h, (oy + STRIP_H - y) / s + 1);
  for (int r = r0; r < r1; r++) {
    const char *row = rows[flip < 0 ? h - 1 - r : r];
    int py = y + r * s;
    for (int c = 0; c < w; c++) {
      char ch = row[flip < 0 ? w - 1 - c : c];
      if (ch != '.') fRect(x + c * s, py, s, s, pal[(uint8_t)ch]);
    }
  }
}

// Draws a sprite centered on (cx, cy)
#define DRAW_CENTERED(name, cx, cy, flip, tint) \
  drawSprite(name, name##_W, name##_H, (cx) - name##_W * SPR_SCALE / 2, (cy) - name##_H * SPR_SCALE / 2, flip, tint)

// flap: 0 up, 1/3 middle, 2 down. flip = -1 at the top of a loop.
// talons = true shows the claws stretched out for a grab.
void drawEagle(int x, int y, uint8_t flap, bool glow, int8_t flip, bool talons) {
  if (!visible(y - 24, y + 24)) return;
  if (glow) {
    uint16_t g = (animT / 3) % 2 ? C_GOLD : C_ORANGE;
    dCirc(x, y, 24, g); dCirc(x, y, 25, g);
  }
  DRAW_CENTERED(EAGLE_BODY, x, y, flip, TINT_NONE);
  if (talons) DRAW_CENTERED(EAGLE_TALONS, x, y, flip, TINT_NONE);
  if (flap == 0) DRAW_CENTERED(EAGLE_WING_UP, x, y, flip, TINT_NONE);
  else if (flap == 2) DRAW_CENTERED(EAGLE_WING_DOWN, x, y, flip, TINT_NONE);
  else DRAW_CENTERED(EAGLE_WING_MID, x, y, flip, TINT_NONE);
}

void drawSmallBug(const Bug &b, uint8_t idx) {
  int x = b.x, y = b.y;
  if (!visible(y - 16, y + 16)) return;
  uint8_t tint = b.burning ? TINT_FIRE : (b.st == B_PARALYZED || b.st == B_FALLING) ? TINT_ZAP : TINT_NONE;
  // falling bugs tumble over and over
  int8_t flip = (b.st == B_FALLING && (animT / 3) % 2) ? -1 : 1;
  DRAW_CENTERED(BUG_BODY, x, y, flip, tint);
  if (b.st == B_ALIVE) {  // buzzing wings
    if (animT & 1) DRAW_CENTERED(BUG_WING_A, x, y, 1, tint);
    else DRAW_CENTERED(BUG_WING_B, x, y, 1, tint);
  }
  if (b.st == B_PARALYZED) {  // electric sparks
    for (uint8_t k = 0; k < 4; k++) {
      uint32_t h = hash32(animT * 7 + idx * 31 + k);
      int sx = x + (int)(h % 25) - 12, sy = y + (int)((h >> 8) % 23) - 11;
      line(sx, sy, sx + 3, sy + 2, C_YELLOW);
      line(sx + 3, sy + 2, sx + 1, sy + 4, C_CYAN);
    }
  }
  if (b.burning) {
    int f = hash32(animT + idx) % 3;
    fTri(x - 5, y - 6, x + 5, y - 6, x + f - 1, y - 16, C_ORANGE);
    fTri(x - 2, y - 6, x + 2, y - 6, x + f - 1, y - 12, C_YELLOW);
  }
}

void drawBigBug(const BigBug &g, uint8_t idx) {
  int x = g.x, y = g.y;
  if (!visible(y - 20, y + 14)) return;
  uint8_t tint = g.flash ? TINT_FLASH : g.burning ? TINT_FIRE : TINT_NONE;
  if ((animT / 4) % 2) DRAW_CENTERED(BEETLE_A, x, y, 1, tint);
  else DRAW_CENTERED(BEETLE_B, x, y, 1, tint);
  // health bar
  fRect(x - 12, y - 18, 24, 4, C_BLACK);
  uint16_t hc = g.hp > 5 ? C_GREEN : g.hp > 2 ? C_YELLOW : C_RED;
  fRect(x - 11, y - 17, max(0, (int)g.hp) * 22 / BIG_BUG_HP, 2, hc);
  if (g.burning) {
    int f = hash32(animT + idx * 13) % 4;
    fTri(x - 10, y - 8, x + 10, y - 8, x + f - 2, y - 24, C_ORANGE);
    fTri(x - 5, y - 8, x + 5, y - 8, x + f - 2, y - 18, C_YELLOW);
  }
}

void drawFish() {
  int x = fish.x, y = fish.y;
  if (!visible(y - 14, y + 14)) return;
  if ((animT / 4) % 2) DRAW_CENTERED(FISH_A, x, y, 1, TINT_NONE);
  else DRAW_CENTERED(FISH_B, x, y, 1, TINT_NONE);
  if ((animT / 4) % 2) {  // sparkle
    hLine(x - 18, y - 10, 5, C_YELLOW); vLine(x - 16, y - 12, 5, C_YELLOW);
    hLine(x + 12, y + 9, 5, C_YELLOW); vLine(x + 14, y + 7, 5, C_YELLOW);
  }
}

void drawFeather(const Feather &f) {
  int x = f.x, y = f.y;
  if (!visible(y - 4, y + 4)) return;
  int len = f.isShort ? 9 : 13, half = len / 2;
  uint16_t vane = f.isShort ? rgb(240, 240, 255) : rgb(255, 220, 120);
  uint16_t shaft = f.isShort ? rgb(150, 150, 190) : rgb(200, 140, 40);
  fTri(x, y, x - half, y - 3, x - half, y + 3, vane);
  fTri(x - half, y - 3, x - half, y + 3, x - len, y, vane);
  line(x - len - 3, y, x, y, shaft);
  if (!f.isShort) { px(x - len - 6, y, vane); px(x - len - 9, y, vane); }
}

void drawFireWave() {
  if (fireWaveX < 0) return;
  int fx = fireWaveX;
  for (int yy = HUD_H + 4; yy < GROUND_Y; yy += 9) {
    if (!visible(yy - 12, yy + 12)) continue;
    int jit = hash32(animT * 131 + yy) % 7;
    fCirc(fx - 20 - jit, yy, 5, rgb(180, 20, 0));
    fCirc(fx - 9 - jit, yy, 7, C_ORANGE);
    fCirc(fx - jit, yy, 5, rgb(255, 170, 0));
    fCirc(fx + 3 - jit, yy, 3, rgb(255, 240, 120));
  }
}

void drawBolts() {
  if (gameMs >= zapShowEnd) return;
  for (uint8_t k = 0; k < zapCount; k++) {
    for (uint8_t s = 0; s < 6; s++) {
      int x0 = zapPts[k][s][0], y0 = zapPts[k][s][1];
      int x1 = zapPts[k][s + 1][0], y1 = zapPts[k][s + 1][1];
      line(x0, y0 + 1, x1, y1 + 1, C_CYAN);
      line(x0, y0, x1, y1, C_WHITE);
    }
  }
}

void drawNest() {
  if (!visible(GROUND_Y - 16, GROUND_Y + 6)) return;
  for (int i = 0; i < eggs; i++) {
    int ex = 10 + i * 6, ey = GROUND_Y - 8;
    fCirc(ex, ey, 3, C_CREAM);
    fCirc(ex, ey - 2, 2, C_CREAM);
  }
  fRound(3, GROUND_Y - 6, 38, 9, 4, rgb(110, 70, 30));
  for (int i = 0; i < 5; i++) line(5 + i * 7, GROUND_Y - 5, 11 + i * 7, GROUND_Y + 1, rgb(160, 110, 50));
}

void drawWeaponIcon(uint8_t i, int cx, int cy) {
  switch (i) {
    case 0:
      fTri(cx + 5, cy, cx, cy - 3, cx, cy + 3, C_WHITE);
      fTri(cx, cy - 3, cx, cy + 3, cx - 4, cy, C_WHITE);
      line(cx - 7, cy, cx + 5, cy, C_GREY);
      break;
    case 1:
      fTri(cx + 8, cy, cx + 1, cy - 3, cx + 1, cy + 3, rgb(255, 220, 120));
      fTri(cx + 1, cy - 3, cx + 1, cy + 3, cx - 6, cy, rgb(255, 220, 120));
      line(cx - 9, cy, cx + 8, cy, rgb(200, 140, 40));
      break;
    case 2:
      fTri(cx - 5, cy + 6, cx + 5, cy + 6, cx, cy - 7, C_RED);
      fTri(cx - 3, cy + 6, cx + 3, cy + 6, cx, cy - 3, C_ORANGE);
      fTri(cx - 1, cy + 6, cx + 2, cy + 6, cx, cy + 1, C_YELLOW);
      break;
    case 3:
      fTri(cx + 2, cy - 7, cx - 4, cy + 1, cx + 1, cy + 1, C_YELLOW);
      fTri(cx - 1, cy - 1, cx + 4, cy - 1, cx - 2, cy + 7, C_YELLOW);
      break;
  }
}

void drawHUD() {
  if (oy >= HUD_H) return;
  char buf[12];
  fRect(0, 0, SCR, HUD_H, C_NAVY);
  hLine(0, HUD_H - 1, SCR, rgb(70, 100, 160));
  text(4, 3, "SCORE", 1, C_GREY);
  snprintf(buf, sizeof(buf), "%d", score);
  text(4, 12, buf, 1, C_WHITE);

  for (int i = 0; i < START_EGGS; i++) {
    int x = 46 + i * 9, y = 11;
    uint16_t c = i < eggs ? C_CREAM : rgb(50, 60, 80);
    fCirc(x, y + 1, 3, c);
    fCirc(x, y - 2, 2, c);
  }

  if (gameMs < powerEnd) {
    int w = (powerEnd - gameMs) * 36 / POWER_MS;
    text(94, 3, "POWER", 1, C_GOLD);
    fRect(94, 13, 36, 4, rgb(60, 50, 0));
    fRect(94, 13, w, 4, C_GOLD);
  }

  // weapon boxes 1-4; fire and electric fill up as they recharge
  for (uint8_t i = 0; i < 4; i++) {
    int bx = 146 + i * 23, by = 2;
    uint16_t bg = rgb(25, 40, 75);
    fRound(bx, by, 21, 18, 3, bg);
    drawWeaponIcon(i, bx + 10, by + 9);
    uint32_t readyAt = i == 2 ? fireReadyAt : i == 3 ? zapReadyAt : 0;
    uint32_t total = i == 2 ? FIRE_RECHARGE : ZAP_RECHARGE;
    if (gameMs < readyAt) {
      int h = 16 * (readyAt - gameMs) / total;
      fRect(bx + 1, by + 1, 19, h, bg);
    }
    if (boxFlash[i]) {                       // just shot
      dRound(bx, by, 21, 18, 3, C_YELLOW);
      dRound(bx + 1, by + 1, 19, 16, 2, C_YELLOW);
    } else if (i >= 2 && gameMs >= readyAt) { // special is charged
      dRound(bx, by, 21, 18, 3, C_GREEN);
    } else {
      dRound(bx, by, 21, 18, 3, rgb(70, 90, 130));
    }
  }
}

// ---------------- Drawing: scenes ----------------
void drawBackground() {
  int y0 = oy, y1 = min(oy + STRIP_H, GROUND_Y);
  for (int y = y0; y < y1; y++) hLine(0, y, SCR, skyCol[y]);

  if (visible(30, 70)) {  // sun
    fCirc(205, 50, 15, rgb(255, 235, 170));
    fCirc(205, 50, 12, rgb(255, 250, 210));
  }
  for (Cloud &c : clouds) {
    if (!visible(c.y - c.r - 2, c.y + c.r + 4)) continue;
    fCirc(c.x, c.y, c.r, C_WHITE);
    fCirc(c.x + c.r, c.y + 2, c.r - 1, C_WHITE);
    fCirc(c.x - c.r, c.y + 3, c.r - 2, C_WHITE);
  }
  if (visible(GROUND_Y - 45, GROUND_Y)) {  // hills
    uint16_t far = rgb(130, 175, 205), nearC = rgb(80, 150, 95);
    for (int x = 0; x < SCR; x++) vLine(x, GROUND_Y - hillFar[x], hillFar[x], far);
    for (int x = 0; x < SCR; x++) vLine(x, GROUND_Y - hillNear[x], hillNear[x], nearC);
  }
  if (visible(GROUND_Y - 6, SCR)) {  // ground
    fRect(0, GROUND_Y, SCR, 5, rgb(60, 170, 60));
    fRect(0, GROUND_Y + 5, SCR, SCR - GROUND_Y - 5, rgb(120, 80, 40));
    int off = (int)(scrollX * 1.5f) % 20;
    for (int gx = -off; gx < SCR; gx += 20) {
      fTri(gx, GROUND_Y, gx + 3, GROUND_Y - 5, gx + 6, GROUND_Y, rgb(40, 130, 40));
      px(gx + 10, GROUND_Y + 12, rgb(90, 60, 30));
      px(gx + 15, GROUND_Y + 19, rgb(160, 120, 70));
    }
  }
}

void drawWorld() {
  drawNest();
  if (fish.active) drawFish();
  for (uint8_t i = 0; i < MAX_BIG; i++) if (bigs[i].active) drawBigBug(bigs[i], i);
  for (uint8_t i = 0; i < MAX_BUGS; i++) if (bugs[i].st != B_DEAD) drawSmallBug(bugs[i], i);
  for (Feather &f : shots) if (f.active) drawFeather(f);
  float sdx, sdy; int8_t flip;
  stuntPose(sdx, sdy, flip);
  uint8_t flap = stunting ? 1 : (animT / 3) % 4;   // wings spread during a flip
  drawEagle(eagleX + sdx, eagleY + sdy, flap, gameMs < powerEnd, flip, stunting);
  drawFireWave();
  drawBolts();
  for (Particle &p : parts) {
    if (!p.life) continue;
    if (p.size > 1) fRect(p.x, p.y, 2, 2, p.col); else px(p.x, p.y, p.col);
  }
  for (Popup &p : pops) {
    if (!p.life) continue;
    char buf[6];
    snprintf(buf, sizeof(buf), "+%d", p.val);
    text(p.x - 6, p.y, buf, 1, C_YELLOW);
  }
  if (eggFlash & 2) {  // red flash when an egg is stolen
    fRect(0, HUD_H, SCR, 3, C_RED);
    fRect(0, GROUND_Y - 3, SCR, 3, C_RED);
    fRect(0, HUD_H, 3, GROUND_Y - HUD_H, C_RED);
    fRect(SCR - 3, HUD_H, 3, GROUND_Y - HUD_H, C_RED);
  }
}

void drawTitle() {
  char buf[20];
  snprintf(buf, sizeof(buf), "BEST %d", best);
  text(6, 6, buf, 1, C_NAVY);
  textShadowC(26, "SKY", 4, C_YELLOW);
  textShadowC(62, "GUARD", 4, C_WHITE);
  textC(98, "TFT EDITION", 1, C_NAVY);
  int ex = 120 + sinf(animT * 0.03f) * 70;
  int ey = 127 + sinf(animT * 0.09f) * 4;
  drawEagle(ex, ey, (animT / 3) % 4, false, 1, false);

  fRound(12, 144, 216, 62, 6, C_NAVY);
  textC(151, "Stick: fly   Click: talon flip", 1, C_WHITE);
  textC(163, "1 Short  2 Long  3 Fire  4 Zap", 1, C_WHITE);
  textC(175, "5 Pause", 1, C_GREY);
  if ((animT / 12) % 2) textC(191, "PRESS STICK TO START", 1, C_YELLOW);
}

void drawPause() {
  fRound(40, 88, 160, 64, 8, C_NAVY);
  dRound(40, 88, 160, 64, 8, C_YELLOW);
  textC(100, "PAUSED", 3, C_WHITE);
  textC(134, "Press 5 to resume", 1, C_GREY);
}

void drawGameOver() {
  char buf[20];
  fRound(24, 56, 192, 130, 10, C_NAVY);
  dRound(24, 56, 192, 130, 10, C_RED);
  textC(68, "GAME OVER", 3, C_RED);
  snprintf(buf, sizeof(buf), "Score: %d", score);
  textC(102, buf, 2, C_WHITE);
  snprintf(buf, sizeof(buf), "Best: %d", best);
  textC(124, buf, 1, C_GREY);
  if (newBest && (millis() / 300) % 2) textC(140, "NEW BEST!", 2, C_YELLOW);
  if (millis() - overAt > 1200 && (millis() / 400) % 2) textC(168, "Press stick", 1, C_WHITE);
}

void render() {
  for (oy = 0; oy < SCR; oy += STRIP_H) {
    drawBackground();
    if (state == ST_TITLE) {
      drawTitle();
    } else {
      drawWorld();
      drawHUD();
      if (state == ST_PAUSE) drawPause();
      if (state == ST_OVER) drawGameOver();
    }
    tft.drawRGBBitmap(0, oy, cv->getBuffer(), SCR, STRIP_H);
  }
}

// ---------------- Setup & loop ----------------
void setup() {
  Serial.begin(115200);

  for (Button *b : allBtns) pinMode(b->pin, INPUT_PULLUP);
  analogReadResolution(12);

  // joystick center calibration (don't touch the stick while booting)
  long sx = 0, sy = 0;
  for (int i = 0; i < 16; i++) { sx += analogRead(JOY_X); sy += analogRead(JOY_Y); delay(2); }
  jcx = sx / 16; jcy = sy / 16;

  // Wiring check (open Serial Monitor at 115200 to see it)
  Serial.printf("\n[check] joystick center X=%d Y=%d (expect ~1500-2500 each)\n", jcx, jcy);
  const char *names[] = {"SW (stick click)", "Button 1", "Button 2", "Button 3", "Button 4", "Button 5"};
  for (int i = 0; i < 6; i++)
    Serial.printf("[check] %-16s GPIO %2d: %s\n", names[i], allBtns[i]->pin,
                  digitalRead(allBtns[i]->pin) == LOW ? "PRESSED/SHORTED to GND?" : "ok (not pressed)");

  tft.init(240, 240);
  tft.setSPISpeed(40000000);   // lower to 27000000 if the screen shows glitches
  tft.setRotation(0);
  tft.fillScreen(C_BLACK);

  cv = new GFXcanvas16(SCR, STRIP_H);
  if (!cv || !cv->getBuffer()) {
    tft.setTextColor(C_RED); tft.setCursor(10, 10); tft.print("Out of memory");
    while (true) delay(1000);
  }

  for (int y = 0; y < GROUND_Y; y++) {
    float t = (float)y / GROUND_Y;
    skyCol[y] = rgb(30 + t * 140, 90 + t * 130, 190 + t * 60);
  }
  randomSeed(esp_random());
  for (Cloud &c : clouds) c = {randf(0, SCR), randf(HUD_H + 15, 110), randf(0.2f, 0.5f), (uint8_t)random(5, 10)};
  updateScenery(0);
  buildPalettes();

  prefs.begin("skyguard", false);
  best = prefs.getInt("best", 0);
}

void loop() {
  static uint32_t lastFrame = 0;
  updateSound();
  uint32_t now = millis();
  if (now - lastFrame < FRAME_MS) return;
  uint32_t dt = min<uint32_t>(now - lastFrame, 60);
  lastFrame = now;

  readButtons();

  switch (state) {
    case ST_TITLE:
      animT++;
      updateScenery(0.6f);
      if (bJoy.pressed) startGame();
      break;
    case ST_PLAY:
      if (b5.pressed) { state = ST_PAUSE; PLAY(S_PAUSE); break; }
      updateGame(dt);
      break;
    case ST_PAUSE:
      if (b5.pressed) { state = ST_PLAY; PLAY(S_PAUSE); }
      break;
    case ST_OVER:
      updateEffects();
      if (millis() - overAt > 1200 && bJoy.pressed) state = ST_TITLE;
      break;
  }

  render();
}
