# MatrixForge

A zero-dependency WS2812B LED matrix display library for Arduino and ESP32.

No FastLED. No Adafruit NeoPixel. Just plug in your matrix and start drawing.

---

## Features

- **Zero external dependencies** — only requires the Arduino core
- **Hardware-accelerated on ESP32** via the RMT peripheral (jitter-free output)
- **Bit-bang fallback** for AVR (cycle-counted ASM) and generic ARM
- **Rich drawing API**: pixels, lines, rectangles, circles, triangles, flood fill
- **Text rendering** with a built-in 4×6 pixel font
- **Sprite system** with per-sprite transparent color
- **Canvas save/restore** (`pushCanvas` / `popCanvas`)
- **HSV → RGB helper** and named colors (`CRGB::Red`, `CRGB::Blue`, …)

---

## Hardware

| Item | Value |
|------|-------|
| Matrix size | 16 × 16 (256 LEDs) — configurable in `config.h` |
| LED type | WS2812B (GRB order) |
| Data pin | GPIO 10 by default — change `MATRIXFORGE_LED_DATA_PIN` in `config.h` |
| Power | 5 V, up to ~4 A at full white brightness |

---

## Installation

### Arduino Library Manager
1. Open Arduino IDE → **Sketch → Include Library → Manage Libraries…**
2. Search for **MatrixForge** and click **Install**.

### Manual
1. Download this repository as a ZIP.
2. Arduino IDE → **Sketch → Include Library → Add .ZIP Library…**
3. Select the downloaded ZIP.

---

## Quick Start

```cpp
#include "MForgeDisplay.h"

MForgeDisplay display;

void setup() {
    display.begin();
}

void loop() {
    display.clearDisplay();

    // Draw a red pixel at (3, 3)
    display.drawPixel(3, 3, 255, 0, 0);

    // Draw a blue rectangle
    display.setFgColor(0, 0, 255);
    display.drawRect(1, 1, 14, 14);

    // Print white text at (0, 0)
    display.setFgColor(255, 255, 255);
    display.drawText(0, 0, "Hi!");

    display.show();
    delay(100);
}
```

---

## Configuration (`config.h`)

Copy `config.h` into your sketch folder and adjust to match your hardware:

```cpp
#define MATRIXFORGE_LED_DATA_PIN   10      // WS2812B data pin
#define MATRIXFORGE_GRID_WIDTH     16      // matrix columns
#define MATRIXFORGE_GRID_HEIGHT    16      // matrix rows
#define MATRIXFORGE_BRIGHTNESS     64      // 0–255 global brightness
```

---

## API Reference

### Init & display
| Method | Description |
|--------|-------------|
| `begin()` | Initialize driver and clear the LED buffer |
| `show()` | Flush the pixel buffer to the LED strip |
| `clearDisplay()` | Fill buffer with black |
| `fillDisplay(r, g, b)` | Fill buffer with a solid color |
| `pushCanvas()` / `popCanvas()` | Save and restore the current buffer |

### Color & cursor
| Method | Description |
|--------|-------------|
| `setFgColor(r, g, b)` | Set foreground color for subsequent draws |
| `setBgColor(r, g, b)` | Set background color |
| `setCursor(x, y)` | Move the text cursor |
| `setBrightness(b)` | Set global brightness (0–255) |

### Drawing
| Method | Description |
|--------|-------------|
| `drawPixel(x, y)` | Draw a pixel in the current fg color |
| `drawPixel(x, y, r, g, b)` | Draw a pixel in an explicit color |
| `drawLine(x0, y0, x1, y1)` | Bresenham line |
| `drawRect(x, y, w, h)` | Hollow rectangle |
| `fillRect(x, y, w, h)` | Filled rectangle |
| `drawCircle(cx, cy, r)` | Hollow circle |
| `fillCircle(cx, cy, r)` | Filled circle |
| `drawTriangle(x0,y0, x1,y1, x2,y2)` | Hollow triangle |
| `floodFill(x, y, r, g, b)` | Flood-fill from (x, y) |

### Bitmaps & sprites
| Method | Description |
|--------|-------------|
| `drawBitmap(x, y, bitmap, w, h)` | Blit a `CRGB[]` array |
| `drawBitmap1bit(x, y, bits, w, h)` | Blit a 1-bit (monochrome) bitmap |
| `drawSprite(sprite, x, y)` | Blit a `MForgeSprite` (respects transparency) |

### Text
| Method | Description |
|--------|-------------|
| `drawChar(c)` | Draw a character at the current cursor |
| `drawText(str)` | Draw a string at the current cursor |
| `drawText(x, y, str)` | Draw a string at (x, y) |
| `drawTextWrapped(x, y, str)` | Draw a string with word-wrap |
| `textWidth(str)` | Return pixel width of a string |

---

## File structure

```
MatrixForge/
├── src/
│   ├── MForgeColor.h       CRGB struct + HSV helper
│   ├── MForgeDriver.h/.cpp WS2812B hardware driver (ESP32 RMT / AVR / ARM)
│   ├── MForgeDisplay.h/.cpp Full drawing API
│   ├── MForgeFont.h        Built-in 4×6 pixel font
│   ├── MForgeSprite.h/.cpp Sprite system with transparency
│   └── config.h            Hardware pin/size defaults
└── examples/
    └── PixelFight/         Two-player territory game demo
```

---

## Example: PixelFight

See [`examples/PixelFight/`](examples/PixelFight/) for a complete two-player game built on this library — featuring territory control, bullets, OLED score display, and buzzer feedback.

---

## License

MIT — see [LICENSE](LICENSE).
