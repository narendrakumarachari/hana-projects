# PixelFight Example

A two-player territory-control game for the MForgeDisplay library.

## Hardware required

- ESP32 (or compatible board)
- 16×16 WS2812B LED matrix
- 1.3" SH1106 OLED display (I2C, 128×64)
- 2× controllers with 3 color buttons + 5 direction buttons each
- Passive buzzer (optional)

## Dependencies

Install via Arduino Library Manager before compiling:

- **Adafruit GFX Library**
- **Adafruit SH110X**

## Pin mapping

See `config.h` in this folder. All hardware pins are defined there.

## How to play

| Action | Player 1 | Player 2 |
|--------|----------|----------|
| Move left/right | LEFT / RIGHT | LEFT / RIGHT |
| Shoot | any color button | any color button |
| Menu / restart | MENU | MENU |

Each player occupies a row at the top (P1) or bottom (P2) of the matrix. Shoot bullets into the opponent's territory to destroy their blocks. Capture all 7 columns to win.
