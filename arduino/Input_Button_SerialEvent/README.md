# Input_Button_SerialEvent

> A debounced push button that sends `BUTTON_PRESSED` and `=` over USB serial each time it is pressed. Probably meant to be read by a program on the PC.

| | |
|---|---|
| **Old name** | `keyboard2345` |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Last edited** | 2026-07-20 |

## What it does
- Reads a button on D11 with a proper 50 ms software debounce (`millis()` based, no `delay`).
- On each **press** (not release), it prints two lines at 9600 baud:
  ```
  BUTTON_PRESSED
  =
  ```

## Parts
- 1 × push button

## Wiring
| Button | Arduino pin |
|---|---|
| One leg | D11 |
| Other leg | GND (uses `INPUT_PULLUP`) |

## Code review notes
- The debounce is textbook-correct and worth reusing.
- ❓ **What was it for?** The old name "keyboard" and the `=` output suggest a PC-side script (Python, Processing or similar) listened on the COM port and typed a key or pressed "=" on a calculator. The Uno can't act as a USB keyboard by itself. That script isn't in this folder, so **write down what it was** before you forget.

## To-do
- [ ] Record, or add to this folder, the PC-side program that read this output.

## Libraries to install

**Headers included:** none

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. No extra libraries needed. Everything used is built into the board package.
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
