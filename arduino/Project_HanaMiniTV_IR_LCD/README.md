# Project_HanaMiniTV_IR_LCD

> "Hana TV": a pretend television on a 16×2 LCD, controlled by the IR remote. It has 9 channels of animations and mini-games, plus volume, pause, channel up/down and an emergency stop.

| | |
|---|---|
| **Old name** | `minitv1245` |
| **Board** | Arduino Uno (uses 59% of flash) |
| **Libraries** | **IRremote** 4.7.1, **LiquidCrystal_I2C** 1.1.2, Wire |
| **Last edited** | 2026-07-28 |

## Channels
| # | Channel | What you see |
|---|---|---|
| 1 | Horse | 2-frame galloping horse (4×2 custom characters) running across |
| 2 | Chrome Dino | The Chrome dinosaur game with cacti and a score. It auto-jumps, and you can also jump manually |
| 3 | Hero Runner | A running man jumping over terrain blocks. It auto-jumps, and you can also jump manually |
| 4 | Butterfly | Life cycle: egg → caterpillar → cocoon → butterfly |
| 5 | Weather | Sunny, cloudy, rain, storm, snow, with icons |
| 6 | Heartbeat | Beating heart, "72 BPM" |
| 7 | Sine wave | Scrolling `-^-_` wave |
| 8 | Matrix rain | Random characters |
| 9 | Showcase | Cycles through channels 1–5 automatically |

## Remote buttons
| Button | Action |
|---|---|
| POWER | TV on (`Hana TV Welcomes you!`) / off (`See you!`) |
| 1 – 9 | Tune to that channel |
| ⏮ PREVIOUS / ⏭ NEXT or ST/REPT | Channel down / up (wraps around 1↔9) |
| VOL+ / VOL− | "Volume" 0–10 (in channels 2 and 3, VOL+ means **jump**) |
| ⏯ PLAY/PAUSE | Pause/resume (in channels 2 and 3 it means **jump**) |
| FUNC/STOP | **Emergency stop**: blank screen for 5 s |

Codes are listed in [`IR_RemoteButtons_LCD/README.md`](../IR_RemoteButtons_LCD/README.md).

## Parts
- 16×2 I2C LCD (0x27)
- IR receiver module + kit remote
- 1 × **passive** buzzer

## Wiring
| Part | Arduino pin |
|---|---|
| IR receiver OUT | D2 |
| Passive buzzer + | D8 |
| LCD SDA / SCL | A4 / A5 |
| A0 | leave unconnected (random seed) |

## Code review notes
- ⚠️ **Showcase (channel 9) corrupts graphics.** The LCD has only 8 custom-character slots. Dino and Hero Runner load their characters only once (`dinoInited` / `heroInited`), but in Showcase the Horse and Butterfly channels overwrite the same slots. When Showcase comes back to Dino or Hero, they draw with the wrong characters. Fix: reset `dinoInited` and `heroInited` to `false` whenever Showcase changes sub-channel.
- ⚠️ **Several texts are longer than 16 characters** and get cut off: `STAGE 4: BUTTERFLY` (18), `Temp: 28C Sky: Clear` (20), `Temp: 22C Wind: 12m/s` (21), `Temp: 18C Rain: Heavy` (21), `WARNING: Lightning!` (19), `PULSE RATE: 72 BPM` (18).
- Channels 1, 4, 5, 6, 7 and 8 call `lcd.clear()` and `createChar()` on every frame, which causes visible flicker. See `Game_FlappyBird_LCD` for a flicker-free approach.
- "Volume" can't change loudness on a passive buzzer. It only changes the **pitch** of the beep (440 + 60 × level Hz), and 0 means mute.
- Emergency stop uses `delay(5000)`, so the remote is ignored for 5 s.

## To-do
- [ ] Fix Showcase character corruption (reset the `…Inited` flags).
- [ ] Shorten every LCD string to 16 characters or fewer.
- [ ] Reduce flicker (avoid `lcd.clear()` every frame).

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`, `IRremote.hpp`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
   - **IRremote** by shirriff, z3t0, ArminJo (4.7.1, must be 4.x)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
