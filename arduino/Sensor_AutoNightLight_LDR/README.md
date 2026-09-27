# Sensor_AutoNightLight_LDR

> An automatic night light: a light sensor (LDR) sets an LED to full, half or off depending on how dark it is.

| | |
|---|---|
| **Old name** | `nightligt6700` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-19 |

## What it does
Reads the LDR on A0 every 100 ms and prints the value at 9600 baud.

| LDR reading | Meaning (in this circuit) | LED on D11 |
|---|---|---|
| 650 – 849 | dark / night | full brightness (255) |
| 850 – 979 | dim / evening | half (128) |
| 980 + | bright / day | off |
| below 650 | *not handled* | keeps its last value |

In this circuit a **higher reading means more light**.

## Parts
- 1 × LDR (photoresistor) + 10 kΩ resistor as a voltage divider
- 1 × LED + 220 Ω

## Wiring
| Part | Arduino pin |
|---|---|
| LDR + 10 kΩ divider midpoint | A0 |
| LED + (through 220 Ω) | D11 (PWM) |

The thresholds only make sense with the original divider. Rerun `SmartHouse_v1/Jun22b_LDR_Light_Serial` to recalibrate.

## Code review notes
- ⚠️ **Readings below 650 do nothing.** That is the darkest range, where the light should be at full brightness. Change the first test to `if (ldrValue < 850)`.
- This is the first step of the theft-alarm series: `Security_ObjectRemovedAlarm` → `Security_NightTheftAlarm` → `Security_TheftDetector_PoliceSiren`.

## To-do
- [ ] Fix the "below 650" gap.
- [ ] Optional: fade smoothly with `map()` instead of 3 fixed steps.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
