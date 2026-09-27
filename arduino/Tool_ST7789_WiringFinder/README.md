# Tool_ST7789_WiringFinder

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/screen-wiring-finder.html)

> A screen-debugging tool for the 1.54" ST7789 TFT on the ESP32. It tries the correct wiring and the 5 most common wire mix-ups one after another, so you can see which one lights the screen.

| | |
|---|---|
| **Old name** | `TFTTest` |
| **Board** | **ESP32 Dev Module** |
| **Libraries** | **Adafruit ST7735 and ST7789** 1.11.0, **Adafruit GFX** 1.12.6, SPI |
| **Last edited** | 2026-09-26 |
| **Made for** | [`SkyGuardTFT`](../SkyGuardTFT) |

## What it does
For each "try" it builds the display driver on **software SPI** (so any pin can take any role), then fills the screen red, green and blue with `TEST n` in large letters. It prints the try's name at **115200 baud**, and loops forever.

| TEST | Assumes… |
|---|---|
| 1 | correct wiring, SPI mode 0 |
| 2 | correct wiring, SPI mode 3 |
| 3 | SCL and SDA swapped |
| 4 | DC and CS swapped |
| 5 | DC and RST swapped |
| 6 | CS and RST swapped |

**Whichever TEST number lights up tells you which wires to fix.**

## Expected (correct) wiring
| TFT | ESP32 |
|---|---|
| SCL | GPIO 18 |
| SDA | GPIO 23 |
| RST | GPIO 4 |
| DC | GPIO 2 |
| CS | GPIO 5 |
| VCC, BL | 3.3V |
| GND | GND |

## To-do
- [ ] Nothing required. Keep it with the SkyGuard project.

## Libraries to install

**Headers included:** `Adafruit_GFX.h`, `Adafruit_ST7789.h`, `SPI.h`

1. Install the **esp32 by Espressif Systems** board package (see [LIBRARIES.md → Step 2](../LIBRARIES.md#step-2-install-the-board-packages)), then select **Tools → Board → esp32 → ESP32 Dev Module**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Adafruit ST7735 and ST7789 Library** by Adafruit (1.11.0). Click **Install All** to also get **Adafruit GFX Library** and **Adafruit BusIO**
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
