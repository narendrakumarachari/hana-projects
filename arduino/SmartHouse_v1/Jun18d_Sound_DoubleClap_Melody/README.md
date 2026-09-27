# Jun18d_Sound_DoubleClap_Melody

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/l-jun18d-double-clap-tune.html)

> Double clap within 1.5 s plays a short C-E-G-C-G-E-C melody.

| | |
|---|---|
| **Old name** | `sketch_jun18d` |
| **Board** | Arduino Uno |
| **Wiring** | Sound DO D12, LED D13, passive buzzer D11 |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
`buzzerPin` is not set with `pinMode()`, but `tone()` sets it itself, so it still works.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
