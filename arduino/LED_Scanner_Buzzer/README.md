# LED_Scanner_Buzzer

> A "Knight Rider" light: a band of 3 LEDs sweeps left and right across 10 LEDs, and each position plays a note.

| | |
|---|---|
| **Old name** | `ledunison353` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-25 |

## What it does
- Lights the LED at the current position plus both neighbours, so 3 LEDs are lit.
- Sweeps from pin 4 to pin 13 and back, 80 ms per step.
- Each position plays one note of a scale (C4 D4 E4 F4 G4 A4 B4 C5 D5 E5) for 70 ms, so the sweep sounds like a rising and falling scale.

## Parts
- 10 × LEDs + 10 × 220 Ω resistors
- 1 × **passive** buzzer (it needs `tone()`; an active buzzer can only beep one pitch)

## Wiring
| Part | Arduino pin |
|---|---|
| LED 1 … LED 10 (+ leg, through 220 Ω) | D4, D5, D6, D7, D8, D9, D10, D11, D12, D13 |
| All LED − legs | GND |
| Passive buzzer + | D3 |
| Passive buzzer − | GND |

## Code review notes
- Works as written.
- D13 is also the on-board "L" LED, so it blinks too.
- This is the simple version of [`LED_Scanner_DualBuzzer_Show`](../LED_Scanner_DualBuzzer_Show).

## To-do
- [ ] Optional: make the 80 ms speed a named constant, or read it from a potentiometer.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
