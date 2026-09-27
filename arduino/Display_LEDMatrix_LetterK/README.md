# Display_LEDMatrix_LetterK

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/led-matrix-k.html)

> Shows the letter **K** on an 8×8 LED matrix driven by a MAX7219 chip.

| | |
|---|---|
| **Old name** | `matrix15678423` |
| **Board** | Arduino Uno |
| **Libraries** | **LedControl** 1.0.6 |
| **Last edited** | 2026-06-30 |

## What it does
Wakes up the MAX7219, sets medium brightness (8 of 15), clears it, and draws this 8×8 bitmap once:
```
. # . . . # . .
. # . . # . . .
. # . # . . . .
. # # . . . . .
. # # . . . . .
. # . # . . . .
. # . . # . . .
. # . . . # . .
```
`loop()` is empty, so the letter just stays on.

## Parts
- 1 × MAX7219 8×8 LED matrix module

## Wiring
| MAX7219 module | Arduino pin |
|---|---|
| DIN | D12 |
| CLK | D11 |
| CS / LOAD | D10 |
| VCC / GND | 5V / GND |

## Code review notes
- Works. The bitmap array is named `one`, but it draws a **K**, so rename it `letterK`.
- Depending on how the module is mounted, the letter may appear rotated or mirrored.
- **MD_Parola** and **MD_MAX72XX** are also installed. They make scrolling text easy (e.g. "HAPPY BIRTHDAY").

## To-do
- [ ] Rename the array `one` to `letterK`.
- [ ] Optional: scroll a name with MD_Parola.

## Libraries to install

**Headers included:** `LedControl.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LedControl** by Eberhard Fahle (1.0.6)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
