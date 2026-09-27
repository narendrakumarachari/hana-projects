# Sound_ClapSensor_MarioMelody

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/clap-mario.html)

> Plays the Super Mario Bros. theme on a buzzer, controlled by a sound sensor: the music plays while the sensor output is HIGH and stops when it goes LOW.

| | |
|---|---|
| **Old name** | `buzz6796` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-17 |

## What it does
- While the sensor's DO pin reads **HIGH**: the LED is on and the Mario opening melody plays note by note (120 ms each), without blocking, using `millis()`.
- When DO reads **LOW**: the music stops, the LED turns off, the song rewinds to the start, `Clap Detected!` is printed, and it waits 300 ms.

## Parts
- 1 × sound sensor module with DO pin
- 1 × LED + 220 Ω (or the on-board LED on D13)
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| Sound sensor DO | D12 |
| LED + | D13 |
| Passive buzzer + | D8 |
| GND of all parts | GND |

## Code review notes
- ⚠️ **The logic and the messages disagree with the other clap sketches.** Here HIGH plays music and prints `No Clap Detected`, and LOW prints `Clap Detected!`. In `Sound_ClapDetect_LED_Buzzer`, HIGH means a clap. So either this sensor module was active-LOW (the behaviour is then "clap to stop the music"), or the two branches are swapped. **Test with the real sensor and write down which one it is.**
- `Serial.println("No Clap Detected")` runs on every loop pass (thousands of times per second) and floods the Serial Monitor. Print only when the state changes.
- The note playback is non-blocking, which is good. It's the same technique used later in `SmartHouse_v1`.

## To-do
- [ ] Confirm the sensor polarity and fix the branch labels or comments to match.
- [ ] Print only when the state changes, not on every loop.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
