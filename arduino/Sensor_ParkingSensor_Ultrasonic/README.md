# Sensor_ParkingSensor_Ultrasonic

> A car parking sensor: the buzzer beeps faster as an object gets closer, and sounds continuously when very close.

| | |
|---|---|
| **Old name** | `car33` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-19 |

## What it does
Measures distance with an HC-SR04 and prints it at 9600 baud.

| Distance | Buzzer |
|---|---|
| > 50 cm | silent |
| 30 – 50 cm | beep every 1 s |
| 15 – 30 cm | beep every 0.5 s |
| 5 – 15 cm | beep every 0.2 s |
| ≤ 5 cm | continuous |

## Parts
- 1 × HC-SR04 ultrasonic sensor
- 1 × **active** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| HC-SR04 VCC / GND | 5V / GND |
| HC-SR04 TRIG | D9 |
| HC-SR04 ECHO | D10 |
| Active buzzer + | D13 |

## Code review notes
- ⚠️ **Bug: nothing in range makes it buzz continuously.** `pulseIn()` has no timeout, so when nothing echoes back it waits 1 s and returns `0`. Distance 0 falls into the "≤ 5 cm" branch, so the buzzer stays on. Fix: `pulseIn(ECHO_PIN, HIGH, 30000)`, and treat `0` as "far away". `SmartHouse_v1` and `Door_Servo_UltrasonicAutoOpen` already do this.
- The speed of sound is written as `0.0343` cm/µs, which is correct.

## To-do
- [ ] Add the `pulseIn` timeout and treat 0 as far (see above).
- [ ] Optional: add an LED bar (green / yellow / red) for a visual distance.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
