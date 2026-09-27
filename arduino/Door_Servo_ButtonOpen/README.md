# Door_Servo_ButtonOpen

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/button-door.html)

> Press a button and a servo "door" opens slowly, stays open 5 seconds, then closes slowly.

| | |
|---|---|
| **Old name** | `Sweep` (it began as the built-in Arduino *Servo → Sweep* example and was then rewritten) |
| **Board** | Arduino Uno |
| **Libraries** | **Servo** 1.3.0 (installed 2026-09-26) |
| **Last edited** | 2026-06-29 |

## What it does
1. On power-up, the door closes (servo at 0°) and it prints `Door Ready` at 9600 baud.
2. On a button **press** (edge-detected, 30 ms debounce):
   - opens from 0° to 90°, one degree every 15 ms (about 1.4 s),
   - stays open for 5 s,
   - closes from 90° back to 0°.

## Parts
- 1 × SG90 (or similar) hobby servo
- 1 × push button

## Wiring
| Part | Arduino pin |
|---|---|
| Servo signal (orange/yellow) | D10 |
| Servo + (red) | 5V |
| Servo − (brown/black) | GND |
| Button, one leg | D9 |
| Button, other leg | GND (uses `INPUT_PULLUP`) |

> The pictures in `images/` are from the **original Arduino Sweep example** (servo on pin 9, no button). They do **not** match this circuit. They are kept for reference only.

## Code review notes
- `const int servoPin = 10;` is declared, but `doorServo.attach(10)` uses the literal `10`. Use `attach(servoPin)`.
- The door blocks while it moves (`delay`), so the button is ignored during the ~8 s cycle. That's fine for this project.

## To-do
- [ ] Change `attach(10)` to `attach(servoPin)`.
- [ ] Optional: draw a real wiring diagram for this circuit and replace the old example images.

## Libraries to install

**Headers included:** `Servo.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Servo** by Michael Margolis, Arduino (1.3.0)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
