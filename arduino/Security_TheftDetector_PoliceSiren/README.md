# Security_TheftDetector_PoliceSiren

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/police-siren-theft-detector.html)

> "Smart Theft Detection System": the finished version of the security series. It adds a street light that follows daylight, a night-time object guard, and a police siren with flashing red and blue lights.

| | |
|---|---|
| **Old name** | `final12345` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-23 |

## What it does
Every 3 s it reads the LDR and the distance, then prints both at 9600 baud.

| LDR reading | Mode | Street light (D11) | Theft guard |
|---|---|---|---|
| 650 – 849 | Night | full | **armed**: object > 3 cm away → `THEFT DETECTED!` and siren |
| 850 – 979 | Evening | half | off |
| 980 + | Day | off | off |
| < 650 | "Below threshold" | off | off |

**Police siren:** the passive buzzer sweeps 500 → 1500 Hz with the red LED on, then 1500 → 500 Hz with the blue LED on (about 0.5 s in total).

## Parts
- 1 × LDR + 10 kΩ divider
- 1 × LED + 220 Ω (street light)
- 1 × RGB LED (only the red and blue legs are used) + resistors
- 1 × HC-SR04
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| LDR divider midpoint | A0 |
| Street-light LED + | D11 (PWM) |
| RGB red | D4 |
| RGB blue | D5 |
| Passive buzzer + | D13 |
| HC-SR04 TRIG / ECHO | D9 / D10 |

## Code review notes
- Best of the series: it has a `getDistance()` helper, a `policeSiren()` function, and handles every LDR range.
- ⚠️ The siren plays **once per 3-second check** (0.5 s of sound, 3 s of silence). A thief hears a chirp, not a continuous alarm. Shorten the delay while in alarm, or latch the alarm on until reset.
- ⚠️ "Below threshold" (< 650) switches the light **off**. In this circuit that is the *darkest* range, so the street light should probably be fully on there (see `Sensor_AutoNightLight_LDR`).
- `pulseIn` has no timeout (see `Security_ObjectRemovedAlarm`).

## To-do
- [ ] Latch the alarm until a reset button is pressed.
- [ ] Decide what "< 650" means for your LDR and fix the light for that range.
- [ ] Add the `pulseIn` timeout.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
