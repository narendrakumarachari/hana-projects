# Game_FlappyBird_LCD

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/flappy-bird-lcd.html)

> Flappy Bird on a 16×2 LCD: push the joystick up to flap, and fly through the gaps in the pipes. It speeds up as you go.

| | |
|---|---|
| **Old name** | `flappybird0000` |
| **Board** | Arduino Uno |
| **Libraries** | **LiquidCrystal_I2C** 1.1.2, Wire |
| **Last edited** | 2026-07-15 |

## How to play
- The bird sits in column 3. **Push the joystick up** to put it on the top row. After 250 ms it falls back to the bottom row ("gravity").
- Each pipe blocks either the top or the bottom row. Be in the open row when a pipe reaches you.
- +1 point per pipe passed. The game starts at 320 ms per step and speeds up by 2 ms per step, down to 140 ms.
- On a crash, the screen shows a dead-bird icon, `GAME OVER`, the score and the high score. Click the joystick to play again.

## Parts
- 16×2 I2C LCD (0x27, or 0x3F)
- Analog joystick module

## Wiring
| Part | Arduino pin |
|---|---|
| LCD SDA / SCL | A4 / A5 |
| Joystick VRy | A1 |
| Joystick SW | D3 |
| A0 | leave unconnected (random seed) |

## Code review notes
- Nicely structured. `buildFrame()` + `render()` draw into a frame buffer and only update cells that changed, so there is **no flicker**. Reuse this technique in the other LCD games.
- Wing-flap animation (2 custom characters) runs independently of the game speed.
- The high score lives in RAM only and resets on power-off. The ESP32 `Preferences` or Uno `EEPROM` library could keep it.

## To-do
- [ ] Optional: save the high score in EEPROM.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
