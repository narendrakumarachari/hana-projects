# Security_NightTheftAlarm

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/night-theft-alarm.html)

> Combines the night light and the object-removed alarm: at night it turns on a "street light" and arms the theft alarm. In the evening and during the day the alarm is off.

| | |
|---|---|
| **Old name** | `seal888` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-23 |

## What it does
Every **3 seconds** it reads the LDR and the distance, then prints both.

| LDR reading | Mode | LED (D11) | Alarm |
|---|---|---|---|
| 650 – 849 | Night | full | **armed**: buzzer on if the object is > 5 cm away |
| 850 – 979 | Evening | half | off |
| 980 + | Day | off | off |
| < 650 | *not handled* | unchanged | unchanged |

## Parts
- 1 × LDR + 10 kΩ divider
- 1 × LED + 220 Ω ("street light")
- 1 × HC-SR04
- 1 × **active** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| LDR divider midpoint | A0 |
| LED + | D11 (PWM) |
| Active buzzer + | D13 |
| HC-SR04 TRIG / ECHO | D9 / D10 |

## Code review notes
- ⚠️ Readings **below 650** (the darkest range) are not handled, the same gap as in `Sensor_AutoNightLight_LDR`.
- ⚠️ The **3-second** `delay` means a thief has up to 3 s before anything happens, and the alarm can't be silenced quickly.
- The `pulseIn` has no timeout (see `Security_ObjectRemovedAlarm`).
- Superseded by [`Security_TheftDetector_PoliceSiren`](../Security_TheftDetector_PoliceSiren), which fixes the "< 650" gap and adds a siren.

## To-do
- [ ] Keep it as a history step, or delete it in favour of the PoliceSiren version.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
