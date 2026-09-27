# Sound_LoudnessAlarm_Analog

> Reads the sound level as a number (0–1023) and flashes an LED and beeps when it reaches 625 or more.

| | |
|---|---|
| **Old name** | `soundtime55fun` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-18 |

## What it does
About once a second, it reads the sensor's **analog** output (AO), prints `Value: N` at 9600 baud, and if N ≥ 625 flashes the LED and active buzzer once (200 ms).

## Parts
- 1 × sound sensor module with an AO pin
- 1 × LED (or the on-board LED on D13)
- 1 × **active** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| Sound sensor AO | A0 |
| LED + | D13 |
| Active buzzer + | D11 |

## Code review notes
- ⚠️ It samples only **once per second** (`delay(1000)`), so a short clap between samples is missed. For a real loudness alarm, sample continuously and keep the loudest value seen each second.
- The threshold `625` is a magic number tied to one sensor and trimmer setting. Make it a named constant.
- The raw-reading step before this is in `SmartHouse_v1/Jun18e_Sound_AnalogLevel_Serial`.

## To-do
- [ ] Sample faster (for example, every 5 ms) and track the peak.
- [ ] Move `625` into a `const int THRESHOLD`.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
