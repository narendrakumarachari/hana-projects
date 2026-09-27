# LED_Scanner_DualBuzzer_Show

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/led-light-show.html)

> A 10-LED light show with sound (scanner sweep, wave fill, centre burst and blink finale), written for two passive buzzers.

| | |
|---|---|
| **Old name** | `ledunison123` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-25 |

## What it does
The show loops through 4 acts:
1. **Scanner**: a 3-LED band sweeps left, right, left. Buzzer 1 plays a rising scale while buzzer 2 plays it falling.
2. **Wave** (4 times): the LEDs fill one by one, then empty in reverse, with pitch sweeps.
3. **Centre expand** (3 times): the light spreads from the middle pair (D7 and D8) out to both ends.
4. **Blink finale**: all 10 LEDs flash 8 times with a high double beep.

## Parts
- 10 × LEDs + 10 × 220 Ω resistors
- 2 × **passive** buzzers

## Wiring
| Part | Arduino pin |
|---|---|
| LED 1 … LED 10 (+ leg, through 220 Ω) | D4 … D13 |
| Buzzer 1 + | D2 |
| Buzzer 2 + | D3 |
| All − legs | GND |

## Code review notes
- ⚠️ **Buzzer 2 is almost always silent.** On an Uno, the built-in `tone()` can play only **one pin at a time**. A `tone()` call on a second pin has no effect while the first pin is still playing. Here `tone(buzzer1, …, 70)` is followed immediately by `tone(buzzer2, …, 70)`, so the second call is ignored.
  - Fix options: (a) use the third-party **Tone** library, which drives up to 3 pins on separate timers; (b) take turns between the buzzers instead of playing both at once; (c) use one buzzer.
- Act 3 hard-codes pin numbers (`digitalWrite(7, HIGH)` …), so moving the LEDs breaks it. Use `ledPins[3]`, `ledPins[4]`, … instead.

## To-do
- [ ] Choose a fix for the two-buzzer limitation (see above).
- [ ] In "Center Expand", replace the hard-coded pin numbers with `ledPins[]` indexes.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
