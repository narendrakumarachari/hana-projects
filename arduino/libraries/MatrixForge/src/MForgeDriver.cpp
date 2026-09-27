// =====================================================
// MForgeDriver.cpp
// =====================================================

#include "MForgeDriver.h"

// =====================================================
// ██████████  ESP32 / ESP32-S3  (RMT)
// =====================================================
#if defined(ESP32)

#include <driver/rmt.h>

// RMT channel to use (0-7 on most ESP32)
#define MATRIXFORGE_RMT_CHANNEL  RMT_CHANNEL_0

// 80 MHz RMT clock → 1 tick = 12.5 ns
// T0H = 32 ticks ≈ 400 ns
// T0L = 68 ticks ≈ 850 ns
// T1H = 64 ticks ≈ 800 ns
// T1L = 36 ticks ≈ 450 ns
#define T0H  32
#define T0L  68
#define T1H  64
#define T1L  36

static rmt_item32_t _bit0 = {{ T0H, 1, T0L, 0 }};
static rmt_item32_t _bit1 = {{ T1H, 1, T1L, 0 }};

void MForgeDriver::_initRMT()
{
    rmt_config_t cfg;
    cfg.rmt_mode                  = RMT_MODE_TX;
    cfg.channel                   = MATRIXFORGE_RMT_CHANNEL;
    cfg.gpio_num                  = (gpio_num_t)MATRIXFORGE_LED_DATA_PIN;
    cfg.clk_div                   = 1;           // 80 MHz base clock
    cfg.mem_block_num             = 1;
    cfg.tx_config.loop_en         = false;
    cfg.tx_config.carrier_en      = false;
    cfg.tx_config.idle_output_en  = true;
    cfg.tx_config.idle_level      = RMT_IDLE_LEVEL_LOW;
    cfg.tx_config.carrier_level   = RMT_CARRIER_LEVEL_HIGH;

    rmt_config(&cfg);
    rmt_driver_install(MATRIXFORGE_RMT_CHANNEL, 0, 0);
}

void MForgeDriver::begin()   { _initRMT(); }

void MForgeDriver::_showRMT(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    // Each LED = 24 bits, +1 reset item at end
    uint16_t numItems = count * 24 + 1;
    rmt_item32_t* items = (rmt_item32_t*)malloc(numItems * sizeof(rmt_item32_t));
    if (!items) return;

    uint16_t idx = 0;
    for (uint16_t i = 0; i < count; ++i) {
        CRGB c = leds[i].scale(brightness);
        // WS2812B expects GRB order
        uint32_t grb = ((uint32_t)c.g << 16) |
                       ((uint32_t)c.r <<  8) |
                        (uint32_t)c.b;

        for (int8_t bit = 23; bit >= 0; --bit)
            items[idx++] = (grb >> bit) & 1 ? _bit1 : _bit0;
    }

    // Reset pulse: 50 µs low = 4000 ticks at 80 MHz
    items[idx].duration0 = 4000;
    items[idx].level0    = 0;
    items[idx].duration1 = 0;
    items[idx].level1    = 0;

    rmt_write_items(MATRIXFORGE_RMT_CHANNEL, items, numItems, true);
    free(items);
}

void MForgeDriver::show(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    _showRMT(leds, count, brightness);
}


// =====================================================
// ██████████  AVR  (Uno, Mega, Nano — bit-bang ASM)
// =====================================================
#elif defined(__AVR__)

#include <avr/interrupt.h>

void MForgeDriver::begin()
{
    pinMode(MATRIXFORGE_DATA_PIN, OUTPUT);
    digitalWrite(MATRIXFORGE_DATA_PIN, LOW);
}

// Cycle-counted inline ASM for 16 MHz AVR
// Timings verified for 16 MHz (62.5 ns / cycle):
//   T0H ≈ 6 cycles = 375 ns   T0L ≈ 14 cycles = 875 ns
//   T1H ≈ 13 cycles = 812 ns  T1L ≈ 7 cycles  = 437 ns
void MForgeDriver::_showAVR(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    // Port/bit for the data pin
    volatile uint8_t* port = portOutputRegister(digitalPinToPort(MATRIXFORGE_DATA_PIN));
    uint8_t pinMask = digitalPinToBitMask(MATRIXFORGE_DATA_PIN);
    uint8_t hi = *port |  pinMask;
    uint8_t lo = *port & ~pinMask;

    cli();  // Disable interrupts during transmission

    for (uint16_t i = 0; i < count; ++i) {
        CRGB c = leds[i].scale(brightness);

        // Send GRB
        uint8_t bytes[3] = { c.g, c.r, c.b };

        for (uint8_t b = 0; b < 3; ++b) {
            uint8_t val = bytes[b];

            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (val & 0x80) {
                    // T1H: 13 cycles high
                    *port = hi;
                    __asm__ volatile("nop\nnop\nnop\nnop\nnop\n"
                                     "nop\nnop\nnop\nnop\nnop\n"
                                     "nop\nnop\n");
                    *port = lo;
                    // T1L: 7 cycles low (loop overhead covers most)
                    __asm__ volatile("nop\nnop\nnop\nnop\n");
                } else {
                    // T0H: 6 cycles high
                    *port = hi;
                    __asm__ volatile("nop\nnop\nnop\n");
                    *port = lo;
                    // T0L: 14 cycles low
                    __asm__ volatile("nop\nnop\nnop\nnop\nnop\n"
                                     "nop\nnop\nnop\nnop\nnop\n"
                                     "nop\n");
                }
                val <<= 1;
            }
        }
    }

    sei();  // Re-enable interrupts

    delayMicroseconds(50);  // Reset pulse
}

void MForgeDriver::show(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    _showAVR(leds, count, brightness);
}


// =====================================================
// ██████████  Generic / ARM (RP2040, STM32, SAMD...)
// Bit-bang using NOP delay loops — adjust
// MATRIXFORGE_NOP_T0H / T1H in config.h if colors look wrong
// =====================================================
#else

#ifndef MATRIXFORGE_NOP_T0H
  #define MATRIXFORGE_NOP_T0H   2    // NOPs for T0H (~400 ns)
#endif
#ifndef MATRIXFORGE_NOP_T1H
  #define MATRIXFORGE_NOP_T1H   6    // NOPs for T1H (~800 ns)
#endif

void MForgeDriver::begin()
{
    pinMode(MATRIXFORGE_DATA_PIN, OUTPUT);
    digitalWrite(MATRIXFORGE_DATA_PIN, LOW);
}

static inline void _nops(uint8_t n)
{
    while (n--) __asm__ volatile("nop");
}

void MForgeDriver::_writeByte(uint8_t byte)
{
    for (int8_t bit = 7; bit >= 0; --bit) {
        if ((byte >> bit) & 1) {
            digitalWrite(MATRIXFORGE_DATA_PIN, HIGH);
            _nops(MATRIXFORGE_NOP_T1H);
            digitalWrite(MATRIXFORGE_DATA_PIN, LOW);
        } else {
            digitalWrite(MATRIXFORGE_DATA_PIN, HIGH);
            _nops(MATRIXFORGE_NOP_T0H);
            digitalWrite(MATRIXFORGE_DATA_PIN, LOW);
        }
    }
}

void MForgeDriver::_showBitbang(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    noInterrupts();
    for (uint16_t i = 0; i < count; ++i) {
        CRGB c = leds[i].scale(brightness);
        _writeByte(c.g);   // WS2812B: GRB order
        _writeByte(c.r);
        _writeByte(c.b);
    }
    interrupts();
    delayMicroseconds(50);
}

void MForgeDriver::show(const CRGB* leds, uint16_t count, uint8_t brightness)
{
    _showBitbang(leds, count, brightness);
}

#endif  // platform
