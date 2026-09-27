# Sound_RandomBirdChirps

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/bird-chirps.html)

> Makes natural-sounding, random bird chirps from two buzzers, as if two birds are calling from different spots.

| | |
|---|---|
| **Old name** | `birdcalllllls22346454` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-25 |

## What it does
- Picks one of the two buzzers at random.
- Plays a "call" of 1 to 3 chirps. Each chirp sweeps up from about 1.8–2.4 kHz to 3.0–3.8 kHz and back down, with random step sizes and timing so no two calls sound the same.
- Waits a random 0.7–3 s, then repeats.
- Uses the noise on the unconnected pin A0 to seed the random generator, so each power-up sounds different.

## Parts
- 2 × **passive** buzzers (spread apart for a stereo effect)

## Wiring
| Part | Arduino pin |
|---|---|
| Buzzer 1 + | D2 |
| Buzzer 2 + | D3 |
| Both − | GND |
| A0 | **leave unconnected** (random seed) |

## Code review notes
- Works well. Only one buzzer plays at a time, so it avoids the Uno's one-`tone()`-at-a-time limit (see `LED_Scanner_DualBuzzer_Show`).
- The same chirp code is reused in [`Sound_BirdPiano_5Buttons`](../Sound_BirdPiano_5Buttons) as `naturalChirp()`.

## To-do
- [ ] Optional: add an LDR so the birds only sing when it is light ("dawn chorus").

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
