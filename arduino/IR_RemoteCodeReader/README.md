# IR_RemoteCodeReader

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/ir-code-reader.html)

> Prints the hex code of every IR remote button you press. Use it to learn a new remote's codes.

| | |
|---|---|
| **Old name** | `IRHEX123` |
| **Board** | Arduino Uno |
| **Libraries** | **IRremote** 4.7.1 |
| **Last edited** | 2026-07-25 |

## What it does
Decodes each IR signal and prints `decodedRawData` in hex at 9600 baud, for example `BA45FF00`. The on-board LED (D13) flickers when a signal is received (`ENABLE_LED_FEEDBACK`). Commented-out lines can also print the protocol, command and address.

## Parts
- 1 × IR receiver (VS1838B / HX1838 module, 3 pins)
- 1 × IR remote (the small 21-key "Car MP3"-style remote from the Elegoo/Arduino starter kits)

## Wiring
| IR receiver | Arduino pin |
|---|---|
| OUT / S / Y | D2 |
| VCC / + / R | 5V |
| GND / − / G | GND |

## How to use
1. Upload and open the Serial Monitor at 9600 baud.
2. Point the remote at the receiver and press a button.
3. Write the code down. The known codes for the kit remote are in [`IR_RemoteButtons_LCD/README.md`](../IR_RemoteButtons_LCD/README.md).

Holding a button down prints `0`. That is the NEC "repeat" signal, not a new button.

## To-do
- [ ] Nothing required. This is a tool.

## Libraries to install

**Headers included:** `IRremote.hpp`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **IRremote** by shirriff, z3t0, ArminJo (4.7.1, must be 4.x)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
