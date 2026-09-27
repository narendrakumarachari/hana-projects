// Types live in their own tab so the Arduino IDE's auto-generated
// function prototypes can see them.
#pragma once
#include <Arduino.h>

struct Note { uint16_t f, ms; };

enum BugState : uint8_t { B_DEAD, B_ALIVE, B_PARALYZED, B_FALLING };

struct Bug { float x, y, baseY, vy, speed, phase; BugState st; bool burning; uint32_t parEnd; };
struct BigBug { float x, y, speed; int8_t hp; bool active, burning; uint8_t flash; };
struct Fish { float x, y, baseY; bool active; };
struct Feather { float x, y, startX, speed; uint8_t dmg; bool isShort, active; };
struct Particle { float x, y, vx, vy; uint16_t col; uint8_t life, size; };
struct Popup { float x, y; uint8_t life; int8_t val; };
struct Cloud { float x, y, spd; uint8_t r; };
