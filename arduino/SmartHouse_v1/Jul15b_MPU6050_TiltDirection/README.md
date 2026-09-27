# Jul15b_MPU6050_TiltDirection

> Talks to an MPU6050 accelerometer directly over I2C (no library) and prints `LEFT`, `RIGHT`, `UP`, `DOWN` or `CENTER` from the tilt, every 2 s.

| | |
|---|---|
| **Old name** | `sketch_jul15b` |
| **Board** | Arduino Uno |
| **Wiring** | MPU6050 SDA A4, SCL A5, VCC 5V (I2C address 0x68) |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
Could become a tilt controller for the LCD games.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** `Wire.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
