#pragma once

// =====================================================
// MForgeColor.h
// Replaces FastLED's CRGB struct — zero dependencies.
// =====================================================

#include <Arduino.h>

// -----------------------------------------------
// CRGB — 3-byte RGB color
// -----------------------------------------------
struct CRGB
{
    uint8_t r, g, b;

    CRGB() : r(0), g(0), b(0) {}
    CRGB(uint8_t r, uint8_t g, uint8_t b) : r(r), g(g), b(b) {}

    bool operator==(const CRGB& o) const { return r==o.r && g==o.g && b==o.b; }
    bool operator!=(const CRGB& o) const { return !(*this == o); }

    // Scale brightness (0=off, 255=full)
    CRGB scale(uint8_t brightness) const
    {
        return CRGB(
            (uint16_t)r * brightness / 255,
            (uint16_t)g * brightness / 255,
            (uint16_t)b * brightness / 255
        );
    }

    // Named colors
    static const CRGB Black;
    static const CRGB White;
    static const CRGB Red;
    static const CRGB Green;
    static const CRGB Blue;
    static const CRGB Yellow;
    static const CRGB Cyan;
    static const CRGB Magenta;
};

// Definitions (in header — include-guard safe via #pragma once)
inline const CRGB CRGB::Black   {  0,   0,   0};
inline const CRGB CRGB::White   {255, 255, 255};
inline const CRGB CRGB::Red     {255,   0,   0};
inline const CRGB CRGB::Green   {  0, 255,   0};
inline const CRGB CRGB::Blue    {  0,   0, 255};
inline const CRGB CRGB::Yellow  {255, 255,   0};
inline const CRGB CRGB::Cyan    {  0, 255, 255};
inline const CRGB CRGB::Magenta {255,   0, 255};

// -----------------------------------------------
// HSV → RGB helper
// h: 0-255, s: 0-255, v: 0-255
// -----------------------------------------------
inline CRGB hsv2rgb(uint8_t h, uint8_t s, uint8_t v)
{
    if (s == 0) return CRGB(v, v, v);

    uint8_t region  = h / 43;
    uint8_t rem     = (h - (region * 43)) * 6;
    uint8_t p = (uint16_t)v * (255 - s) / 255;
    uint8_t q = (uint16_t)v * (255 - ((uint16_t)s * rem / 255)) / 255;
    uint8_t t = (uint16_t)v * (255 - ((uint16_t)s * (255 - rem) / 255)) / 255;

    switch (region) {
        case 0: return CRGB(v, t, p);
        case 1: return CRGB(q, v, p);
        case 2: return CRGB(p, v, t);
        case 3: return CRGB(p, q, v);
        case 4: return CRGB(t, p, v);
        default:return CRGB(v, p, q);
    }
}

// -----------------------------------------------
// fill_solid helper (replaces FastLED's)
// -----------------------------------------------
inline void fill_solid(CRGB* leds, uint16_t count, CRGB color)
{
    for (uint16_t i = 0; i < count; ++i)
        leds[i] = color;
}
