# LED_RGB_ColorCycle

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/rgb-color-cycle.html)

> Makes an RGB LED show red, then green, then blue, one second each, forever.

| | |
|---|---|
| **Old name** | `TR5` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-14 (one of the first sketches) |

## What it does
Turns each colour of an RGB LED fully on for 1 s, one at a time: red, green, blue, and repeat.

## Parts
- 1 × RGB LED, common cathode (**HIGH = on**)
- 3 × 220 Ω resistors (one per colour leg)

## Wiring
| RGB LED leg | Arduino pin |
|---|---|
| Red   | D9 (through 220 Ω) |
| Green | D10 (through 220 Ω) |
| Blue  | D11 (through 220 Ω) |
| Common (longest leg) | GND |

> With a **common-anode** LED, connect the common leg to 5V instead. HIGH then means off.

## Code review notes
- Works as written.
- Pins 9, 10 and 11 all support PWM, so `analogWrite()` could mix colours. The fade versions in `SmartHouse_v1/Jun14b_LED_RGB_FadeEachColor` and `Jun15a_LED_RGB_Fade_3Rounds` already do this.

## To-do
- [ ] Optional: add yellow, cyan, magenta and white steps by turning on two or three pins at once.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
