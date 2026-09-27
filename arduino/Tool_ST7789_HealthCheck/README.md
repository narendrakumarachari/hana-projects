# Tool_ST7789_HealthCheck

> "Is my 1.54" ST7789 screen dead?" Checks each wire for shorts, asks the screen chip for its ID, then does a colour test, and prints a plain-English verdict.

| | |
|---|---|
| **Old name** | `TFTCheck` |
| **Board** | **ESP32 Dev Module** |
| **Libraries** | **Adafruit ST7735 and ST7789** 1.11.0, **Adafruit GFX** 1.12.6, SPI |
| **Last edited** | 2026-09-26 |
| **Made for** | [`SkyGuardTFT`](../SkyGuardTFT) |

## What it does
Open the Serial Monitor at **115200 baud**, then press EN/RESET on the ESP32.

1. **Wire check**: drives each pin (SCL, SDA, RST, DC, CS) high and low and reads it back. A pin stuck LOW or HIGH points to a short, which is often a burnt chip.
2. **ID check**: sends the ST7789 "Read Display ID" command (`0x04`) by bit-banging, then reads the reply twice, once with a pull-up and once with a pull-down on SDA.
   - Same value both times (not `00000000` / `FFFFFFFF`) → the chip answered (a live ST7789 replies `85 85 52`).
   - The value just follows the pull → nobody answered.
3. **Colour test** (only if it answered): red, green, blue, white, then `ALIVE!` in SPI modes 0 and 3.

It then prints one of three verdicts: **not burnt**, **a wire is shorted** (with how to tell whether it's the screen or the board), or **no answer / inconclusive**.

## Wiring
Same as SkyGuardTFT: SCL 18, SDA 23, RST 4, DC 2, CS 5, VCC and BL to 3.3V.

## Code review notes
- Well written and self-explanatory output.
- Some cheap modules have no readable SDA line, so "did not answer" doesn't *prove* the screen is dead. The sketch says so.

## To-do
- [ ] Nothing required.

## Libraries to install

**Headers included:** `Adafruit_GFX.h`, `Adafruit_ST7789.h`, `SPI.h`

1. Install the **esp32 by Espressif Systems** board package (see [LIBRARIES.md → Step 2](../LIBRARIES.md#step-2-install-the-board-packages)), then select **Tools → Board → esp32 → ESP32 Dev Module**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Adafruit ST7735 and ST7789 Library** by Adafruit (1.11.0). Click **Install All** to also get **Adafruit GFX Library** and **Adafruit BusIO**
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
