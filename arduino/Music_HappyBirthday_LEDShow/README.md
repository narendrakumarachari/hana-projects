# Music_HappyBirthday_LEDShow

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/birthday-light-show.html)

> A birthday treat for Krish: plays Happy Birthday while 10 LEDs dance, then runs a light-and-sound celebration. Repeats forever.

| | |
|---|---|
| **Old name** | `krishbdaytreat454` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-25 |

## What it does
1. Plays the 25-note Happy Birthday melody (C major, starting on G4). On each note, a 3-LED "scanner" band moves one step along the LEDs.
2. **Celebration**:
   - Even and odd LEDs flash alternately 15 times, with two-tone beeps.
   - A single-LED chase runs 4 times with a rising pitch.
   - All LEDs blink 8 times.
3. Waits 3 s, then starts again.

## Parts
- 10 × LEDs + 10 × 220 Ω resistors
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| LED 1 … LED 10 (+ leg, through 220 Ω) | D4 … D13 |
| Passive buzzer + | D3 |
| All − legs | GND |

The wiring matches [`LED_Scanner_Buzzer`](../LED_Scanner_Buzzer), so one breadboard runs both.

## Code review notes
- Works as written.
- It loops forever and only stops when unplugged. Fine for a party, but a start button would be nicer.
- Durations use the "1000 / note type" convention: 4 = quarter note, 8 = eighth, 2 = half.

## To-do
- [ ] Optional: add a push button so each press plays the song once instead of looping.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
