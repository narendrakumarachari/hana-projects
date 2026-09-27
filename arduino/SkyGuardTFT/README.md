# SkyGuardTFT: Sky Guard, TFT edition

> The flagship game. An eagle defends its nest from waves of bugs on a 240×240 colour screen, with 4 feather weapons, a loop-the-loop talon grab, particle effects, sound, and a saved best score. Runs on an ESP32.

| | |
|---|---|
| **Old name** | `SkyGuardTFT` (unchanged; see to-do) |
| **Board** | **ESP32 Dev Module** (esp32 core 3.3.x). Uses 27% of flash |
| **Libraries** | **Adafruit ST7735 and ST7789** 1.11.0, **Adafruit GFX** 1.12.6 (+ **Adafruit BusIO**), SPI, Preferences (built into the ESP32 core) |
| **Last edited** | 2026-09-26 |
| **First version** | [`Game_SkyGuardian_LCD`](../Game_SkyGuardian_LCD) (Uno + 16×2 LCD) |
| **Debug tools** | [`Tool_ST7789_WiringFinder`](../Tool_ST7789_WiringFinder), [`Tool_ST7789_HealthCheck`](../Tool_ST7789_HealthCheck) |

## Files
| File | What's in it |
|---|---|
| `SkyGuardTFT.ino` | All game logic, drawing, sound, input (≈1,070 lines, with the wiring diagram in the header comment) |
| `GameTypes.h` | The structs (`Bug`, `BigBug`, `Fish`, `Feather`, `Particle`, `Popup`, `Cloud`, `Note`). They live in their own tab so the Arduino IDE's auto-generated prototypes can see them |
| `Sprites.h` | Pixel-art sprites as text: each letter is one pixel colour, `.` is transparent. Eagle (body, 3 wing poses, talons), bug (body + 2 wing frames), beetle (2 frames), fish (2 frames) |
| `Upload to ESP32.bat` | Double-click to compile and upload without opening the IDE. It finds the ESP32's COM port automatically (CH340 / CP210x chip) |

## How to play
- **Joystick**: fly the eagle.
- **Joystick click**: **talon flip**, a loop-the-loop (0.5 s) that grabs any small bug within reach and claws big bugs for 5 damage.
- **Button 5**: pause / resume.
- Bugs fly in from the right. Any bug that gets past the left edge steals an egg from your nest. You start with **5 eggs**, and at 0 it's game over.
- Spawning speeds up as your score rises. Bugs also get faster.

| Weapon | Button | Effect | Recharge |
|---|---|---|---|
| 1 Short feather | GPIO 13 | fast, flies ¼ of the screen, **4 dmg** | none |
| 2 Long feather | GPIO 14 | slower, full screen, **2 dmg** | none |
| 3 Fire feather | GPIO 27 | a fire wave sweeps the screen and burns **every bug currently on screen** | **25 s** |
| 4 Electric feather | GPIO 26 | lightning **paralyses the 5 closest small bugs** for 3 s, then they fall (+1 each) | **5 s** |

| Enemy / item | Score |
|---|---|
| Small bug (1 hit) | +1 |
| Big beetle (10 HP, health bar) | +2 |
| Golden fish (fly into it) | 5 s **power-up**: faster eagle, faster feathers, gold glow |

The HUD shows score, eggs, the power-up timer, and 4 weapon boxes. Fire and Zap boxes fill up as they recharge and get a green border when ready. The **best score is saved** in the ESP32's flash (`Preferences`, namespace `skyguard`, key `best`), so it survives power-off.

## Parts
- ESP32 Dev Module (CH340 or CP2102 USB)
- 1.54" 240×240 **ST7789** SPI TFT (7 pins, no CS on some modules)
- Analog joystick module
- 5 × push buttons
- 1 × **passive** buzzer

## Wiring
| TFT | ESP32 | | Joystick | ESP32 |
|---|---|---|---|---|
| GND | GND | | GND | GND |
| VCC | 3.3V | | +5V | **3.3V (NOT 5V!)** |
| SCL | GPIO 18 | | VRx | GPIO 34 (left/right) |
| SDA | GPIO 23 | | VRy | GPIO 35 (up/down) |
| RST | GPIO 4 | | SW | GPIO 32 (talon flip) |
| DC | GPIO 2 | | | |
| CS | GPIO 5 | | | |
| BL | 3.3V | | | |

| Button (pin → button → GND) | ESP32 |
|---|---|
| 1 Short feather | GPIO 13 |
| 2 Long feather | GPIO 14 |
| 3 Fire feather | GPIO 27 |
| 4 Electric feather | GPIO 26 |
| 5 Pause | GPIO 22 |
| Passive buzzer + | GPIO 25 (− to GND) |

- **Don't touch the joystick while booting.** The center position is calibrated at start-up.
- If the eagle moves the wrong way, flip `JOY_SWAP_XY`, `JOY_INVERT_X` or `JOY_INVERT_Y` at the top of the `.ino`.
- If the screen shows glitches, lower `tft.setSPISpeed(40000000)` to `27000000`.
- The Serial Monitor (**115200**) prints a wiring check at boot: joystick centre values, and whether any button looks shorted.

## How it works (for future me)
- **Frame loop**: ~30 fps (`FRAME_MS 33`). `updateGame(dt)` handles the logic, then `render()` draws the screen.
- **No-flicker drawing**: the 240×240 screen is drawn as **6 horizontal strips of 240×40** into an off-screen `GFXcanvas16`. Each strip is then pushed with one `drawRGBBitmap`. Every drawing helper (`fRect`, `fCirc`, …) subtracts the current strip offset `oy`, and `visible()` skips anything outside the strip.
- **Sprites**: `drawSprite()` reads the text art from `Sprites.h` and draws each pixel as a 2×2 block. `buildPalettes()` pre-computes 4 colour sets (normal, blue "zapped", orange "burning", white "hit flash") while keeping outlines dark.
- **Sound**: non-blocking. `PLAY(S_xxx)` queues a `Note[]` sequence and `updateSound()` steps through it each loop.
- **Buttons**: 25 ms debounce, edge-triggered (`pressed` is true for one frame).
- **Scenery**: gradient sky, sun, drifting clouds, two parallax sine-wave hill layers, scrolling grass.

## Uploading
- **Arduino IDE**: board **ESP32 Dev Module**, choose the COM port, then Upload.
- **One-click**: close the Serial Monitor, then double-click `Upload to ESP32.bat`.
  - It expects the Arduino IDE at `C:\Program Files\Arduino IDE\…`. Edit the `CLI=` line if the IDE is installed somewhere else.

## Code review notes
- The cleanest, best-structured code in the collection. Constants are named, the game tuning is grouped, and the comments explain why.
- Uses a fixed pool of objects (no `new` during play), which is good for a microcontroller.
- Minor: `render()` redraws all 6 strips every frame, even on the paused screen. That's fine at 30 fps on an ESP32.

## To-do
- [ ] Optional: rename the folder to `Game_SkyGuard_ESP32_TFT` to match the naming scheme. Close the Arduino IDE first (it was open and locked the folder), then rename **both** the folder and `SkyGuardTFT.ino`. The `.bat` file needs no change.
- [ ] Optional: add a photo of the finished build to this folder.

## Libraries to install

**Headers included:** `Adafruit_GFX.h`, `Adafruit_ST7789.h`, `SPI.h`, `Preferences.h`, `GameTypes.h`, `Sprites.h`

1. Install the **esp32 by Espressif Systems** board package (see [LIBRARIES.md → Step 2](../LIBRARIES.md#step-2-install-the-board-packages)), then select **Tools → Board → esp32 → ESP32 Dev Module**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Adafruit ST7735 and ST7789 Library** by Adafruit (1.11.0). Click **Install All** to also get **Adafruit GFX Library** and **Adafruit BusIO**
3. `GameTypes.h` and `Sprites.h` are part of this project; keep them in this folder.
4. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
