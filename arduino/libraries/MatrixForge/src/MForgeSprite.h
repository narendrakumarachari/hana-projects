#pragma once

// =====================================================
// MForgeSprite.h — no FastLED dependency
// =====================================================

#include <Arduino.h>
#include "MForgeColor.h"
#include "config.h"

class MForgeSprite
{
public:
    MForgeSprite(uint8_t w, uint8_t h);

    uint8_t width()  const { return _w; }
    uint8_t height() const { return _h; }

    void setPixel(uint8_t x, uint8_t y, uint8_t r, uint8_t g, uint8_t b);
    void setPixel(uint8_t x, uint8_t y, CRGB color);

    void fill(uint8_t r, uint8_t g, uint8_t b);
    void fill(CRGB color);
    void clear();

    void setTransparentColor(uint8_t r, uint8_t g, uint8_t b);
    void clearTransparentColor();

    void loadBitmap(const CRGB* bitmap);

    CRGB getPixel(uint8_t x, uint8_t y) const;
    bool isTransparent(uint8_t x, uint8_t y) const;

private:
    uint8_t _w, _h;
    CRGB    _buf[MATRIXFORGE_MAX_SPRITE_W * MATRIXFORGE_MAX_SPRITE_H];
    CRGB    _transparentColor;
    bool    _hasTransparency;
};
