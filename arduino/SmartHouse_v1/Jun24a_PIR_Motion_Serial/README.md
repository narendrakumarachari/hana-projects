# Jun24a_PIR_Motion_Serial

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/l-jun24a-motion.html)

> Prints `Motion Detected!` when the PIR sensor output is HIGH (then waits 1 s).

| | |
|---|---|
| **Old name** | `sketch_jun24a` |
| **Board** | Arduino Uno |
| **Wiring** | PIR OUT D5, VCC 5V |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
PIR modules need about 30-60 s to settle after power-up.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
