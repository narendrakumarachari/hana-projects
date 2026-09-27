# Jun14a_LCD_I2C_PrintName

> Prints a name on line 1 of a 16x2 I2C LCD (address 0x27).

| | |
|---|---|
| **Old name** | `sketch_jun14a` |
| **Board** | Arduino Uno |
| **Wiring** | LCD SDA A4, SCL A5, 5V, GND |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
⚠️ **Does not build** with the standard LiquidCrystal_I2C library: change `lcd.begin();` to `lcd.init();`. See [LIBRARIES.md](../../LIBRARIES.md#4--library-conflict-to-fix). It prints a person's full name, so decide whether that should be public.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
3. Also change `lcd.begin();` to `lcd.init();` or it won't build.
4. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
