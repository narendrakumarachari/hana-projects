# Door_Servo_UltrasonicAutoOpen

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/l-auto-door.html)

> **Automatic door.** When a person is within 20 cm: 3 beeps, the servo opens slowly to 90°, stays 5 s, beeps, closes slowly, then waits until the person leaves before it can trigger again.

| | |
|---|---|
| **Old name** | `servodoor12345678910` |
| **Board** | Arduino Uno |
| **Wiring** | Servo D10, HC-SR04 TRIG D7 / ECHO D6, active buzzer D8 |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
Needs the **Servo** library (see [LIBRARIES.md](../../LIBRARIES.md)). Correctly uses a `pulseIn` timeout.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** `Servo.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Servo** by Michael Margolis, Arduino (1.3.0)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
