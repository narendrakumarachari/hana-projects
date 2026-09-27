#pragma once

// =====================================================
// MForgeDriver.h
// Zero-dependency WS2812B LED output driver.
//
// Automatically selects the best method:
//   ESP32 / ESP32-S3  → RMT peripheral (hardware, jitter-free)
//   AVR (Uno/Mega)    → Bit-bang with cycle-counted ASM
//   Other ARM / etc.  → Bit-bang via GPIO + NOP delays
//
// WS2812B timing (datasheet):
//   T0H = 400 ns  T0L = 850 ns
//   T1H = 800 ns  T1L = 450 ns
//   RES = 50 µs low
//
// Color order: GRB (WS2812B native)
// =====================================================

#include <Arduino.h>
#include "MForgeColor.h"
#include "config.h"

class MForgeDriver
{
public:
    // Call once in setup() — configures pin / RMT channel
    static void begin();

    // Send 'count' CRGB pixels to the strip.
    // Applies global brightness scaling before transmitting.
    static void show(const CRGB* leds, uint16_t count, uint8_t brightness);

private:

#if defined(ESP32)
    // ---- ESP32 RMT implementation ----
    static void _initRMT();
    static void _showRMT(const CRGB* leds, uint16_t count, uint8_t brightness);

#elif defined(__AVR__)
    // ---- AVR bit-bang implementation ----
    static void _showAVR(const CRGB* leds, uint16_t count, uint8_t brightness);

#else
    // ---- Generic bit-bang implementation ----
    static void _showBitbang(const CRGB* leds, uint16_t count, uint8_t brightness);
    static void _writeByte(uint8_t byte);
#endif
};
