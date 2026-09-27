# Security_ObjectRemovedAlarm

> An anti-theft alarm: put a valuable object in front of an ultrasonic sensor, and if it is moved away, the buzzer sounds.

| | |
|---|---|
| **Old name** | `steal777` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-06-19 |

## What it does
Every ~100 ms it measures the distance and prints it at 9600 baud.
- **≤ 10 cm**: the object is there, so it stays quiet.
- **> 10 cm**: the object was removed. It prints `ALARM! Object Removed!` and beeps 5 times (repeating while the object is gone).

## Parts
- 1 × HC-SR04 ultrasonic sensor
- 1 × **active** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| HC-SR04 TRIG | D9 |
| HC-SR04 ECHO | D10 |
| Active buzzer + | D8 |
| VCC / GND | 5V / GND |

## Code review notes
- ⚠️ `pulseIn()` has no timeout. If the sensor gets no echo, it returns `0` → distance 0 → "object present", so the alarm **fails silently**. Use `pulseIn(ECHO_PIN, HIGH, 30000)` and treat `0` as "removed".
- An almost identical copy is `SmartHouse_v1/Jun19a_Ultrasonic_ObjectRemovedAlarm` (threshold 5 cm, buzzer on D13).
- Next step in the series: [`Security_NightTheftAlarm`](../Security_NightTheftAlarm).

## To-do
- [ ] Add the `pulseIn` timeout and treat no echo as an alarm.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
