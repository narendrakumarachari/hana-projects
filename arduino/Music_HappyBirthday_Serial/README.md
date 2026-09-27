# Music_HappyBirthday_Serial

> Type `happy birthday` in the Serial Monitor and a buzzer plays Happy Birthday.

| | |
|---|---|
| **Old name** | `Birthday2` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-16 |

## What it does
Waits for a line of text on the serial port (9600 baud). When the line is `happy birthday` (capitalisation and surrounding spaces don't matter), it plays the 25-note Happy Birthday melody (F major, starting on C4) on a passive buzzer.

## Parts
- 1 × **passive** buzzer

## Wiring
| Buzzer | Arduino pin |
|---|---|
| + | D8 |
| − | GND |

## How to use
1. Upload, then open the Serial Monitor at **9600 baud**.
2. Set the line-ending dropdown (bottom of the Serial Monitor) to **Newline**.
3. Type `happy birthday` and press Enter.

## Code review notes
- Works as written.
- The loop count `25` is hard-coded. `sizeof(notes) / sizeof(notes[0])` would stay correct if notes are added.
- A version with a slightly tighter rhythm is `SmartHouse_v1/Jun16a_Music_HappyBirthday_Serial`. Exact duplicates (`tr66b`, `sketch_jun16b`) were deleted on 2026-09-26.

## To-do
- [ ] Optional: replace the `25` with a computed length.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
