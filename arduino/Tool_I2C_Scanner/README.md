# Tool_I2C_Scanner

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/i2c-scanner.html)

> Finds every I2C device connected to the board and prints its address. Use it when an LCD stays blank or a sensor won't answer.

| | |
|---|---|
| **Old name** | `i2cfind3456` |
| **Board** | Any (Uno used) |
| **Libraries** | Wire (built in) |
| **Last edited** | 2026-07-03 |

## What it does
Scans addresses 1–126 **once** at start-up and prints each one that replies, then `Scan Complete`. Press the board's **RESET** button to scan again.

## Wiring
| I2C device | Uno pin |
|---|---|
| SDA | A4 |
| SCL | A5 |
| VCC / GND | 5V / GND |

## Addresses you will typically see
| Address | Device in these projects |
|---|---|
| `0x27` | 16×2 LCD I2C backpack (PCF8574) |
| `0x3F` | 16×2 LCD I2C backpack (PCF8574A version) |
| `0x68` | MPU6050 accelerometer/gyro (`SmartHouse_v1/Jul15b_…`) |

## To-do
- [ ] Nothing required. This is a tool.

## Libraries to install

**Headers included:** `Wire.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
