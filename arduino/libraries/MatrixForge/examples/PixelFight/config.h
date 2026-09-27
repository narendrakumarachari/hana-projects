#pragma once

// =====================================================
// MatrixForge Configuration
// Hardware Mapping
// =====================================================

// -----------------------------------------------------
// LED Matrix (WS2812B)
// -----------------------------------------------------
#define MATRIXFORGE_LED_DATA_PIN      10

#define MATRIXFORGE_GRID_WIDTH        16
#define MATRIXFORGE_GRID_HEIGHT       16
#define MATRIXFORGE_NUM_LEDS          (MATRIXFORGE_GRID_WIDTH * MATRIXFORGE_GRID_HEIGHT)

#define MATRIXFORGE_BRIGHTNESS        64      // 0-255

// -----------------------------------------------------
// OLED Display (I2C)
// -----------------------------------------------------
#define OLED_SDA_PIN             8
#define OLED_SCL_PIN             9

#define OLED_WIDTH               128
#define OLED_HEIGHT              64

// -----------------------------------------------------
// Buzzer
// -----------------------------------------------------
#define BUZZER_PIN               11

// -----------------------------------------------------
// Controller 1
// -----------------------------------------------------
#define P1_RED_PIN               1
#define P1_GREEN_PIN             2
#define P1_BLUE_PIN              3

#define P1_MENU_PIN              4
#define P1_UP_PIN                5
#define P1_LEFT_PIN              7   // swapped — controller wired opposite
#define P1_RIGHT_PIN             6
#define P1_DOWN_PIN              12

// -----------------------------------------------------
// Controller 2
// -----------------------------------------------------
#define P2_RED_PIN               13
#define P2_GREEN_PIN             14
#define P2_BLUE_PIN              15

#define P2_MENU_PIN              16
#define P2_UP_PIN                17
#define P2_LEFT_PIN              18
#define P2_RIGHT_PIN             21
#define P2_DOWN_PIN              33

// -----------------------------------------------------
// Serial
// -----------------------------------------------------
#define MATRIXFORGE_SERIAL_BAUD       115200

// -----------------------------------------------------
// Drawing Defaults
// -----------------------------------------------------
#define MATRIXFORGE_DEFAULT_FG_R      255
#define MATRIXFORGE_DEFAULT_FG_G      255
#define MATRIXFORGE_DEFAULT_FG_B      255

#define MATRIXFORGE_DEFAULT_BG_R      0
#define MATRIXFORGE_DEFAULT_BG_G      0
#define MATRIXFORGE_DEFAULT_BG_B      0

// -----------------------------------------------------
// Font Settings
// -----------------------------------------------------
#define MATRIXFORGE_FONT_W            4
#define MATRIXFORGE_FONT_H            6
#define MATRIXFORGE_FONT_SPACING      1

// -----------------------------------------------------
// Sprite Limits
// -----------------------------------------------------
#define MATRIXFORGE_MAX_SPRITE_W      16
#define MATRIXFORGE_MAX_SPRITE_H      16

// -----------------------------------------------------
// OLED Address
// Common SSD1306 addresses:
// 0x3C or 0x3D
// -----------------------------------------------------
#define OLED_I2C_ADDRESS         0x3C
#define I2C_SDA                   8
#define I2C_SCL                   9

// -----------------------------------------------------
// System Settings
// -----------------------------------------------------
#define MATRIXFORGE_PLAYER_COUNT      2
#define MATRIXFORGE_USE_BUZZER        1
#define MATRIXFORGE_USE_OLED          1

// -----------------------------------------------------
// Optional Timing Calibration
// Uncomment only if needed for custom bit-bang driver
// -----------------------------------------------------
// #define MATRIXFORGE_NOP_T0H 2
// #define MATRIXFORGE_NOP_T1H 6