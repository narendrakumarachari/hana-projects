# Sound_ClapDetect_LED_Buzzer

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/clap-detector.html)

> When the sound sensor hears a loud noise (a clap), an LED lights and an active buzzer sounds.

| | |
|---|---|
| **Old name** | `save3` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-18 |

## What it does
Reads the sound sensor's **digital** output (DO) every 100 ms. While it reads HIGH (loud), the LED and the buzzer are on and `Clap Detected` is printed at 9600 baud. Otherwise both are off.

## Parts
- 1 × sound sensor module with a DO pin (e.g. KY-038 / LM393 type, with a blue sensitivity trimmer)
- 1 × LED + 220 Ω (or just use the on-board LED on D13)
- 1 × **active** buzzer (beeps on its own when given power)

## Wiring
| Part | Arduino pin |
|---|---|
| Sound sensor DO | D12 |
| Sound sensor VCC / GND | 5V / GND |
| LED + (through 220 Ω) | D13 |
| Active buzzer + | D11 |

## How to use
Turn the sensor's trimmer until its on-board LED is *just* off in a quiet room. A clap should then light it.

## Code review notes
- Works as written.
- Some sensor modules are active-LOW. The code comment says to change `HIGH` to `LOW` if so.
- The step-by-step versions of this are in `SmartHouse_v1/Jun17a_…`, `Jun17b_…`, `Jun18b_…` and `Jun18d_…`.

## To-do
- [ ] Nothing required.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
