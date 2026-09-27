# Sound_BirdPiano_5Buttons

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/bird-piano.html)

> Krish's Bird Piano / communication board: 5 buttons, each playing a different house-sparrow-style call that stands for a word (Food, Water, Play, Scritches, Outside).

| | |
|---|---|
| **Old name** | `birdpiano2345432` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-29 |

## What it does
| Button | Pin | Meaning | Sound |
|---|---|---|---|
| 1 | D2 | **Food** | Rising chirp, 2.5 → 4 kHz in fixed steps |
| 2 | D3 | **Water** | Natural chirp: random up/down sweep, 1 or 2 times |
| 3 | D4 | **Play** | Trill: 5 fast rising sweeps (3–4.5 kHz) |
| 4 | D5 | **Scritches** | Double "cheep": two quick downward slides |
| 5 | D6 | **Outside** | Complex call: double cheep, then natural chirp |

After a sound plays, the buttons are ignored for 0.8 s so one press doesn't repeat.

## Parts
- 5 × push buttons (no resistors needed; internal pull-ups are used)
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| Button 1 … 5 (one leg) | D2, D3, D4, D5, D6 |
| Other leg of every button | GND |
| Passive buzzer + | D9 |
| Passive buzzer − | GND |
| A0 | leave unconnected (random seed) |

Buttons read **LOW when pressed** (`INPUT_PULLUP`).

## Code review notes
- Clean and well commented.
- Sounds are randomised on purpose, so each press sounds a little different.
- Sounds block while playing (`delay`). That's fine here because only one call plays at a time.

## To-do
- [ ] Optional: label the physical buttons with pictures (food bowl, water drop, ball, hand, tree).
- [ ] Optional: log which button is pressed, and when, over Serial to see what gets used most.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
