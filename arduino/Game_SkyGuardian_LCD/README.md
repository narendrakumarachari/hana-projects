# Game_SkyGuardian_LCD

> "Sky Guardian": the first version of the eagle game, on a 16×2 LCD. Fly the eagle with a joystick and shoot the bugs before they reach your nest and steal your eggs.

| | |
|---|---|
| **Old name** | `skyguard13455` |
| **Board** | Arduino Uno |
| **Libraries** | **LiquidCrystal_I2C** 1.1.2, Wire |
| **Last edited** | 2026-07-15 |
| **Later version** | [`SkyGuardTFT`](../SkyGuardTFT) (ESP32 + colour screen) |

## How to play
- Title screen `SKY GUARDIAN / PRESS JOYSTICK`. Click the joystick to start.
- **Joystick** moves the eagle (custom `V` character) anywhere on the 16×2 grid.
- **Long-range button** (D8): the feather flies across the screen, 2 damage.
- **Short-range button** (D9): the feather flies 3 cells, 4 damage.
- Enemies come from the right:

| Symbol | What | Points |
|---|---|---|
| `<` | small bug, dies in 1 hit | +1 |
| `O` | big bug, 10 HP | +2 |
| `*` | fish: fly into it for a 5 s speed boost | — |

- Any bug that reaches the left edge steals one of your **5 eggs**. At 0 eggs it's `GAME OVER`. Click the joystick to go back to the title.

## Parts
- 16×2 I2C LCD (0x27)
- Analog joystick module (VRx, VRy, SW)
- 2 × push buttons
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| LCD SDA / SCL | A4 / A5 |
| Joystick VRx | A0 |
| Joystick VRy | A1 |
| Joystick SW | D3 |
| Long-shot button | D8 → GND |
| Short-shot button | D9 → GND |
| Passive buzzer + | D13 |
| A3 | leave unconnected (random seed) |

## Code review notes
- ⚠️ `lcd.clear()` runs on **every frame** (every ~30 ms), so the screen flickers. `Game_FlappyBird_LCD` solves this by only redrawing cells that changed. Copy that `render()` idea here.
- Much of the code is packed onto single long lines, which is hard to read. Run **Tools → Auto Format** (Ctrl+T) before editing.
- There's no high score. The TFT version keeps one in flash memory.

## To-do
- [ ] Fix the flicker with frame diffing.
- [ ] Auto-format the code.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
