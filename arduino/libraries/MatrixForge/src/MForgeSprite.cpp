// =====================================================
// MForgeSprite.cpp
// =====================================================

#include "MForgeSprite.h"

MForgeSprite::MForgeSprite(uint8_t w, uint8_t h)
    : _w(w < MATRIXFORGE_MAX_SPRITE_W ? w : MATRIXFORGE_MAX_SPRITE_W)
    , _h(h < MATRIXFORGE_MAX_SPRITE_H ? h : MATRIXFORGE_MAX_SPRITE_H)
    , _transparentColor(CRGB::Black)
    , _hasTransparency(false)
{
    clear();
}

void MForgeSprite::setPixel(uint8_t x, uint8_t y, uint8_t r, uint8_t g, uint8_t b)
{
    if (x >= _w || y >= _h) return;
    _buf[y * _w + x] = CRGB(r, g, b);
}

void MForgeSprite::setPixel(uint8_t x, uint8_t y, CRGB color)
{
    if (x >= _w || y >= _h) return;
    _buf[y * _w + x] = color;
}

void MForgeSprite::fill(uint8_t r, uint8_t g, uint8_t b)
{
    fill_solid(_buf, _w * _h, CRGB(r, g, b));
}

void MForgeSprite::fill(CRGB color)
{
    fill_solid(_buf, _w * _h, color);
}

void MForgeSprite::clear()
{
    fill_solid(_buf, _w * _h, CRGB::Black);
}

void MForgeSprite::setTransparentColor(uint8_t r, uint8_t g, uint8_t b)
{
    _transparentColor = CRGB(r, g, b);
    _hasTransparency  = true;
}

void MForgeSprite::clearTransparentColor()
{
    _hasTransparency = false;
}

void MForgeSprite::loadBitmap(const CRGB* bitmap)
{
    memcpy(_buf, bitmap, _w * _h * sizeof(CRGB));
}

CRGB MForgeSprite::getPixel(uint8_t x, uint8_t y) const
{
    if (x >= _w || y >= _h) return CRGB::Black;
    return _buf[y * _w + x];
}

bool MForgeSprite::isTransparent(uint8_t x, uint8_t y) const
{
    if (!_hasTransparency) return false;
    return getPixel(x, y) == _transparentColor;
}
