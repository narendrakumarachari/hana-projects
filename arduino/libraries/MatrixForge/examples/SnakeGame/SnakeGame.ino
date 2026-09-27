// =====================================================
// SnakeGame.ino — MatrixForge Snake — Arduino entry point
//
// File layout:
//   SnakeGame.ino   ← this file (setup + loop only)
//   SnakeGame.h     ← class declaration
//   SnakeGame.cpp   ← full game logic
//   config.h        ← ALL pin & tuning constants
//   MForgeDisplay.h/.cpp  ← LED matrix driver
//   MForgeDriver.h/.cpp   ← WS2812B low-level driver
//   MForgeColor.h         ← CRGB type
//   MForgeFont.h          ← 4×6 bitmap font
//   MForgeSprite.h/.cpp   ← sprite helpers
//   CommandParser.h/.cpp  ← (unused in game, keep in folder)
//
// Libraries required (Arduino IDE Library Manager):
//   • Adafruit SSD1306
//   • Adafruit GFX Library
// =====================================================

#include "config.h"
#include "MForgeDisplay.h"
#include "SnakeGame.h"

// ── Shared hardware objects ───────────────────────
MForgeDisplay   display;
Adafruit_SH1106G oled(
    SNAKE_OLED_WIDTH,
    SNAKE_OLED_HEIGHT,
    &Wire,
    SNAKE_OLED_RESET
);

// ── Game instance ─────────────────────────────────
SnakeGame game(display, oled);

// =====================================================
void setup()
{
    Serial.begin(MATRIXFORGE_SERIAL_BAUD);

    // Initialise LED matrix
    display.begin();
    display.clearDisplay();
    display.show();

    // Initialise OLED
    Wire.begin(8, 9);
    Wire.setClock(100000);
    if (!oled.begin(SNAKE_OLED_ADDR, true))
    {
        Serial.println(F("OLED not found — check wiring & SNAKE_OLED_ADDR in config.h"));
        // Game continues without OLED
    }
    else
    {
        oled.clearDisplay();
        oled.display();
    }

    // Start game (shows title screens)
    game.begin();
}

// =====================================================
void loop()
{
    game.update();
}
