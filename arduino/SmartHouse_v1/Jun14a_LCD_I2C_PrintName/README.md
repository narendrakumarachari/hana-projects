# Jun14a_LCD_I2C_PrintName

> Prints a name on line 1 of a 16x2 I2C LCD (address 0x27).

| | |
|---|---|
| **Old name** | `sketch_jun14a` |
| **Board** | Arduino Uno |
| **Wiring** | LCD SDA A4, SCL A5, 5V, GND |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
✅ Fixed 2026-09-26: it used `lcd.begin();`, which only existed in a duplicate LCD library. It now uses `lcd.init();` like every other LCD sketch. It prints a person's full name (kept by choice).

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
4. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
