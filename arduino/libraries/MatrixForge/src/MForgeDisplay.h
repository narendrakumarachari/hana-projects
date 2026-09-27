#pragma once

// =====================================================
// MForgeDisplay.h
// Full-featured 16×16 LED matrix driver
// Zero external dependencies — uses MForgeDriver
// for WS2812B output and MForgeColor for CRGB.
// =====================================================

#include <Arduino.h>
#include "MForgeColor.h"
#include "MForgeDriver.h"
#include "MForgeFont.h"
#include "MForgeSprite.h"
#include "config.h"

class MForgeDisplay
{
public:
    // ---- Init ----------------------------------------
    void begin();

    // ---- Buffer control ------------------------------
    void show();
    void clearDisplay();
    void fillDisplay(uint8_t r, uint8_t g, uint8_t b);
    void pushCanvas();
    void popCanvas();

    // ---- Brightness ----------------------------------
    void setBrightness(uint8_t b) { _brightness = b; }
    uint8_t getBrightness() const { return _brightness; }

    // ---- Color / cursor state ------------------------
    void setFgColor(uint8_t r, uint8_t g, uint8_t b);
    void setBgColor(uint8_t r, uint8_t g, uint8_t b);
    CRGB getFgColor() const { return _fg; }
    CRGB getBgColor() const { return _bg; }
    void setCursor(int16_t x, int16_t y);
    int16_t getCursorX() const { return _curX; }
    int16_t getCursorY() const { return _curY; }

    // ---- Primitives ----------------------------------
    void drawPixel(int16_t x, int16_t y);
    void drawPixel(int16_t x, int16_t y, uint8_t r, uint8_t g, uint8_t b);
    void drawPixel(int16_t x, int16_t y, CRGB color);

    void drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1);
    void drawLine(int16_t x0, int16_t y0, int16_t x1, int16_t y1,
                  uint8_t r, uint8_t g, uint8_t b);

    void drawRect(int16_t x, int16_t y, int16_t w, int16_t h);
    void drawRect(int16_t x, int16_t y, int16_t w, int16_t h,
                  uint8_t r, uint8_t g, uint8_t b);

    void fillRect(int16_t x, int16_t y, int16_t w, int16_t h);
    void fillRect(int16_t x, int16_t y, int16_t w, int16_t h,
                  uint8_t r, uint8_t g, uint8_t b);

    void drawCircle(int16_t cx, int16_t cy, int16_t radius);
    void drawCircle(int16_t cx, int16_t cy, int16_t radius,
                    uint8_t r, uint8_t g, uint8_t b);

    void fillCircle(int16_t cx, int16_t cy, int16_t radius);
    void fillCircle(int16_t cx, int16_t cy, int16_t radius,
                    uint8_t r, uint8_t g, uint8_t b);

    void drawTriangle(int16_t x0, int16_t y0,
                      int16_t x1, int16_t y1,
                      int16_t x2, int16_t y2);
    void drawTriangle(int16_t x0, int16_t y0,
                      int16_t x1, int16_t y1,
                      int16_t x2, int16_t y2,
                      uint8_t r, uint8_t g, uint8_t b);

    void floodFill(int16_t x, int16_t y, uint8_t r, uint8_t g, uint8_t b);

    // ---- Bitmap blit ---------------------------------
    void drawBitmap(int16_t x, int16_t y,
                    const CRGB* bitmap, uint8_t w, uint8_t h);

    void drawBitmap1bit(int16_t x, int16_t y,
                        const uint8_t* bits, uint8_t w, uint8_t h,
                        bool bgTransparent = false);

    // ---- Sprite blit ---------------------------------
    void drawSprite(const MForgeSprite& sprite, int16_t x, int16_t y);

    // ---- Text ----------------------------------------
    void drawChar(char c, bool bgTransparent = true);
    void drawChar(int16_t x, int16_t y, char c, bool bgTransparent = true);
    void drawText(const char* str, bool bgTransparent = true);
    void drawText(int16_t x, int16_t y, const char* str, bool bgTransparent = true);
    void drawTextWrapped(int16_t x, int16_t y, const char* str, bool bgTransparent = true);
    int16_t textWidth(const char* str) const;

private:
    CRGB    _leds[MATRIXFORGE_NUM_LEDS];
    CRGB    _savedCanvas[MATRIXFORGE_NUM_LEDS];
    uint8_t _brightness = MATRIXFORGE_BRIGHTNESS;
    CRGB    _fg;
    CRGB    _bg;
    int16_t _curX = 0, _curY = 0;

    uint16_t _xyToIndex(int16_t x, int16_t y) const;
    bool     _inBounds (int16_t x, int16_t y) const;
    void     _writePixel(int16_t x, int16_t y, CRGB color);
    void     _circlePoints(int16_t cx, int16_t cy, int16_t dx, int16_t dy, CRGB color);
    void     _hLine(int16_t x0, int16_t x1, int16_t y, CRGB color);
    
};
