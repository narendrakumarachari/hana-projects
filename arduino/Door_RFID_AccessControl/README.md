# Door_RFID_AccessControl

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/rfid-door.html)

> An RFID door lock: tap the right card and the servo door opens with a happy beep. Tap a wrong card and it stays locked with a warning sound.

| | |
|---|---|
| **Old name** | `entercard12345` |
| **Board** | Arduino Uno |
| **Libraries** | **MFRC522** 1.4.12, **Servo** 1.3.0 (installed 2026-09-26), SPI (built in) |
| **Last edited** | 2026-07-23 |

## What it does
1. Waits for an RFID card or tag.
2. Prints the card's UID at 9600 baud, for example `Card UID: F1:8A:BC:5C`.
3. If the UID matches `authorizedUID`:
   - prints `ACCESS GRANTED`, plays a rising two-beep, opens the servo to 90° for 3 s, then closes it.
4. Otherwise:
   - prints `ACCESS DENIED`, plays a low "buzz-buzz-buzzz", and keeps the servo at 0°.

## Parts
- 1 × RC522 RFID reader module (13.56 MHz) + card/key fob
- 1 × SG90 servo
- 1 × **passive** buzzer

## Wiring
| RC522 pin | Arduino pin |
|---|---|
| **3.3V** | **3.3V** (⚠️ *not* 5V) |
| GND | GND |
| SDA (SS) | D10 |
| SCK | D13 |
| MOSI | D11 |
| MISO | D12 |
| RST | D9 |
| IRQ | not connected |

| Other part | Arduino pin |
|---|---|
| Servo signal | D6 |
| Passive buzzer + | D3 |

## How to add your own card
1. Upload, open the Serial Monitor at 9600 baud, and tap the new card.
2. Copy the printed UID, e.g. `A1:B2:C3:D4`.
3. Change the line `byte authorizedUID[] = {0xF1, 0x8A, 0xBC, 0x5C};` to `{0xA1, 0xB2, 0xC3, 0xD4}` and upload again.

## Code review notes
- Clear structure: `checkUID()`, `successBuzzer()` and `wrongBuzzer()` are separate functions.
- Only **one** card is allowed. Supporting several needs an array of UIDs.
- A UID-only check is fine for a toy or model door but not for real security, because card UIDs can be copied.
- The authorised card UID is visible in the public code. That is harmless for a toy, but worth knowing.

## To-do
- [ ] Optional: allow a list of cards, and add a "master card" that adds new cards.

## Libraries to install

**Headers included:** `SPI.h`, `MFRC522.h`, `Servo.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **Servo** by Michael Margolis, Arduino (1.3.0)
   - **MFRC522** by GithubCommunity (1.4.12)
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
