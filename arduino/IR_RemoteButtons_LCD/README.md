# IR_RemoteButtons_LCD

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/ir-remote-lcd.html)

> Press a button on the IR remote and its name (POWER, VOL+, 1, 2, …) appears on a 16×2 LCD and in the Serial Monitor.

| | |
|---|---|
| **Old name** | `remoteHEXir34` (an identical copy, `hexmap123`, was deleted on 2026-09-26) |
| **Board** | Arduino Uno |
| **Libraries** | **IRremote** 4.7.1, **LiquidCrystal_I2C** 1.1.2 (Frank de Brabander / marcoschwartz), Wire (built in) |
| **Last edited** | 2026-07-28 |

## What it does
- Shows `IR Remote / Ready` at start-up.
- For each known code, shows `Button:` on line 1 and the name on line 2.
- Unknown codes show `Unknown` plus the hex code.

## Parts
- 1 × IR receiver module + the kit remote
- 1 × 16×2 LCD with I2C backpack (address **0x27**; some are 0x3F, check with `Tool_I2C_Scanner`)

## Wiring
| Part | Arduino pin |
|---|---|
| IR receiver OUT | D2 |
| LCD SDA | A4 |
| LCD SCL | A5 |
| LCD & IR VCC / GND | 5V / GND |

## Remote code table (IRremote 4.x `decodedRawData`, kit 21-key remote)
| Button | Code | In this sketch? |
|---|---|---|
| POWER | `0xBA45FF00` | ✅ |
| VOL+ | `0xB946FF00` | ✅ |
| FUNC/STOP | `0xB847FF00` | ✅ |
| ⏮ PREVIOUS | `0xBB44FF00` | ✅ |
| ⏯ PLAY/PAUSE | `0xBF40FF00` | ✅ |
| ⏭ NEXT | `0xBC39FF00` | ❌ (found in `Project_HanaMiniTV_IR_LCD`) |
| ▲ UP | `0xF609FF00` | ✅ |
| ▼ DOWN | `0xF807FF00` | ✅ |
| VOL− | `0xEA15FF00` | ✅ |
| ST/REPT | `0xF20DFF00` | ✅ ("Repeat") |
| 0 | `0xE916FF00` | ✅ |
| 1 | `0xF30CFF00` | ✅ |
| 2 | `0xE718FF00` | ✅ |
| 3 | `0xA15EFF00` | ✅ |
| 4 | `0xF708FF00` | ✅ |
| 5 | `0xE31CFF00` | ✅ |
| 6 | `0xA55AFF00` | ✅ |
| 7 | `0xBD42FF00` | ✅ |
| 8 | `0xAD52FF00` | ❌ (found in `Project_HanaMiniTV_IR_LCD`) |
| 9 | `0xB54AFF00` | ✅ |
| EQ | *not recorded yet* | ❌ |

## Code review notes
- ⚠️ **Typo:** just before `case 0xF20DFF00:` there is a stray `0` on its own line followed by `;`. It compiles (as a do-nothing statement) but should be deleted.
- Buttons **8** and **NEXT** are missing (codes above). EQ was never captured.
- Holding a button sends a repeat code (`0`), which shows as `Unknown 0`. Ignore it with `if (IrReceiver.decodedIRData.flags & IRDATA_FLAGS_IS_REPEAT)`.
- The name "Up" is mixed case while the others are uppercase.

## To-do
- [ ] Remove the stray `0` / `;` line.
- [ ] Add 8 (`0xAD52FF00`), NEXT (`0xBC39FF00`) and EQ (use `IR_RemoteCodeReader` to capture it).
- [ ] Ignore repeat codes.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`, `IRremote.hpp`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
   - **IRremote** by shirriff, z3t0, ArminJo (4.7.1, must be 4.x)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
