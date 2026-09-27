# Jun17a_Sound_ClapDetect_Serial

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/l-jun17a-clap.html)

> Prints `Clap Detected` when the sound sensor's digital output goes HIGH.

| | |
|---|---|
| **Old name** | `sketch_jun17a` |
| **Board** | Arduino Uno |
| **Wiring** | Sound sensor DO D12 |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
If your module is active-LOW, change `HIGH` to `LOW`.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
