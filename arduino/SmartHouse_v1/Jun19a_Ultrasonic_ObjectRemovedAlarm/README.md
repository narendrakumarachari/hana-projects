# Jun19a_Ultrasonic_ObjectRemovedAlarm

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/l-jun19a-object-alarm.html)

> Beeps 5 times whenever the object in front of the HC-SR04 is more than 5 cm away (anti-theft).

| | |
|---|---|
| **Old name** | `sketch_jun19a` |
| **Board** | Arduino Uno |
| **Wiring** | TRIG D9, ECHO D10, active buzzer D13 |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
Same as top-level `Security_ObjectRemovedAlarm` (which uses 10 cm and buzzer D8). No `pulseIn` timeout: no echo reads as 0 cm, meaning "present".

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
