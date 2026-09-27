#pragma once

#include <Arduino.h>
#include "MForgeDisplay.h"
#include "config.h"

// OLED support — SH110X driver (e.g. 1.3" 128×64 I2C OLED)
#include <Adafruit_GFX.h>
#include <Adafruit_SH110X.h>

class PixelFightGame
{
public:
    PixelFightGame();

    void begin();
    void update();
    void render();

private:

    // ==========================================
    // Constants
    // ==========================================
    static const uint8_t WIDTH  = 16;
    static const uint8_t HEIGHT = 16;

    static const uint8_t P1_TOP_ROW = 0;
    static const uint8_t P2_TOP_ROW = 15;

    static const uint8_t TERRITORY_P1_START = 1;
    static const uint8_t TERRITORY_P1_END   = 7;

    static const uint8_t TERRITORY_P2_START = 8;
    static const uint8_t TERRITORY_P2_END   = 14;

    static const uint16_t SHOOT_COOLDOWN  = 180;
    static const uint16_t MOVE_DEBOUNCE_MS = 160;

    // Territory blocks vs player pixels — must be visually distinct
    static const uint8_t BLUE_BLOCK_R  = 0,   BLUE_BLOCK_G  = 0,   BLUE_BLOCK_B  = 255;
    static const uint8_t BLUE_PLAYER_R = 255, BLUE_PLAYER_G = 255, BLUE_PLAYER_B = 0;
    static const uint8_t RED_BLOCK_R   = 255, RED_BLOCK_G   = 0,   RED_BLOCK_B   = 0;
    static const uint8_t RED_PLAYER_R  = 0,   RED_PLAYER_G  = 255, RED_PLAYER_B  = 255;

    static const uint8_t TEAM_BLUE = 1;
    static const uint8_t TEAM_RED  = 2;

    static const uint8_t CELL_INTACT      = 0;
    static const uint8_t CELL_HIT_BY_RED  = 1;
    static const uint8_t CELL_HIT_BY_BLUE = 2;

    // ==========================================
    // Bullet
    // ==========================================
    struct Bullet
    {
        bool active;
        int8_t x;
        int8_t y;
        int8_t dir;
        uint8_t owner;
    };

    // ==========================================
    // Players
    // ==========================================
    int8_t p1X;
    int8_t p2X;

    uint16_t p1Score;
    uint16_t p2Score;

    bool gameOver;
    uint8_t winner;

    // territory state (INTACT or destroyed-by-opponent color)
    uint8_t p1Territory[16][7];
    uint8_t p2Territory[16][7];

    unsigned long winAnimStart;
    unsigned long lastOledUpdate;

    Bullet bulletP1;
    Bullet bulletP2;

    unsigned long lastShotP1;
    unsigned long lastShotP2;

    MForgeDisplay display;

    // OLED display object — SH110X, 128×64, I2C, no hardware reset pin
    Adafruit_SH1106G oled{OLED_WIDTH, OLED_HEIGHT, &Wire, -1};

    // ==========================================
    // Core
    // ==========================================
    void resetGame();

    void updateInputs();
    void updateBullets();

    void fireP1();
    void fireP2();

    void checkVictory();
    void showSplashOLED();
    void updateScoreOLED();
    void showWinnerOLED();
    void renderWinnerAnimation();

    void oledPrintCentered(int16_t areaX, int16_t areaW, int16_t y,
                           uint8_t textSize, const char* text);
    void oledPrintCentered(int16_t areaX, int16_t areaW, int16_t y,
                           uint8_t textSize, uint16_t value);
    void oledDrawHudFrame();
    void oledDrawOddsBar(int16_t x, int16_t y, int16_t w, int16_t h, uint8_t pct);

    // ==========================================
    // Drawing
    // ==========================================
    void drawPlayers();
    void drawTerritory();
    void drawBullets();

    // ==========================================
    // Helpers
    // ==========================================
    bool pressed(uint8_t pin);

    void damageP1(uint8_t column);
    void damageP2(uint8_t column);

    void repairP1(uint8_t column);
    void repairP2(uint8_t column);

    bool columnDestroyedP1(uint8_t column);
    bool columnDestroyedP2(uint8_t column);

    void computeWinChance(uint8_t& bluePct, uint8_t& redPct) const;
};
