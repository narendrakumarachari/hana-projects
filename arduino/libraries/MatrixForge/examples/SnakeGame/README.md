# SnakeGame Example

A single-player Snake game for the MatrixForge library.

## Hardware required

- ESP32 (or compatible board)
- 16×16 WS2812B LED matrix
- 1.3" SH1106 OLED display (I2C, 128×64)
- 1× controller with UP / DOWN / LEFT / RIGHT / MENU buttons
- Passive buzzer (optional)

## Dependencies

Install via Arduino Library Manager before compiling:

- **Adafruit GFX Library**
- **Adafruit SH110X**

## Pin mapping

All hardware pins are defined in `config.h` — adjust `SNAKE_BTN_*` to match your wiring.

## How to play

| Action | Button |
|--------|--------|
| Steer the snake | UP / DOWN / LEFT / RIGHT |
| Start / restart | MENU |

Eat the orange food pellets to grow and score points. Hitting a wall or yourself ends the game. Your score is shown live on the OLED display.
