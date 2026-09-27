# LCD_SerialMessageBoard

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/lcd-message-board.html)

> Type a message in the Serial Monitor and it appears on a 16×2 LCD.

| | |
|---|---|
| **Old name** | `LCDMSG25434` |
| **Board** | Arduino Uno |
| **Libraries** | **LiquidCrystal_I2C** 1.1.2, Wire (built in) |
| **Last edited** | 2026-07-15 |

## What it does
- Shows `Send msg via / Serial Monitor` at start-up.
- Collects characters until Enter (newline or carriage return), then clears the LCD and shows the message:
  - up to 16 characters: line 1 only;
  - 17–32 characters: split across both lines;
  - anything past 32 characters is cut off.

## Parts
- 1 × 16×2 LCD with I2C backpack (address 0x27; change to 0x3F if the screen stays blank)

## Wiring
| LCD | Arduino pin |
|---|---|
| SDA | A4 |
| SCL | A5 |
| VCC / GND | 5V / GND |

## How to use
Serial Monitor at **9600 baud**, line ending **Newline**. Type and press Enter.

## Code review notes
- Works as written.
- Splitting at exactly 16 characters can cut a word in half.
- If the text is still blank with the right address, turn the blue contrast trimmer on the back of the I2C backpack.

## To-do
- [ ] Optional: word-wrap at spaces, and scroll messages longer than 32 characters.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
