#pragma once
// =====================================================
// SnakeGame.h — Single-player Snake for MatrixForge
// Depends on: MForgeDisplay, Adafruit SSD1306/GFX
// All tunable constants live in config.h
// =====================================================

#include <Arduino.h>
#include "config.h"
#include "MForgeDisplay.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

// ── Game states ───────────────────────────────────
enum class GameState : uint8_t
{
    TITLE,      // waiting on title screen
    PLAYING,    // active game
    DEAD        // game-over screen
};

// ── 2-D grid point ────────────────────────────────
struct Point
{
    int8_t x, y;

    bool operator==(const Point& o) const { return x == o.x && y == o.y; }
};

// =====================================================
// SnakeGame class
// =====================================================
class SnakeGame
{
public:
    // Pass references to the shared display and OLED
    SnakeGame(MForgeDisplay& disp, Adafruit_SH1106G& oled);

    // Call once in setup()
    void begin();

    // Call every loop() — handles input + ticks internally
    void update();

private:
    // ── External hardware refs ────────────────────
    MForgeDisplay&     _disp;
    Adafruit_SH1106G& _oled;

    // ── Snake data ────────────────────────────────
    Point   _snake[SNAKE_MAX_LENGTH];
    int16_t _len;
    Point   _food;
    int8_t  _dirX, _dirY;        // current direction
    int8_t  _nextDirX, _nextDirY; // buffered next direction

    // ── Game state ────────────────────────────────
    GameState    _state;
    int16_t      _score;
    unsigned long _lastTick;

    // ── Input ─────────────────────────────────────
    void _readButtons();
    bool _menuPressed();         // debounced MENU read

    // ── Game logic ────────────────────────────────
    void _resetGame();
    void _tick();
    void _placeFood();
    bool _selfCollision(Point p) const;

    // ── Rendering ────────────────────────────────
    void _drawMatrix();
    void _flashDead();
    void _drawTitleMatrix();

    // ── OLED screens ─────────────────────────────
    void _oledTitle();
    void _oledScore();
    void _oledGameOver();

    // ── Buzzer ────────────────────────────────────
    void _beepEat();
    void _beepDead();
    void _beepStart();
};
