# Aug16a_ESP32_WiFi_LED_WebAPI

> Wi-Fi web server with `/on`, `/off` and `/PoP` (blink once) to control an LED. Earlier version of the top-level `ESP32_WiFi_LED_WebAPI`.

| | |
|---|---|
| **Old name** | `sketch_aug16a` |
| **Board** | ESP32 Dev Module |
| **Wiring** | LED on GPIO 23 |
| **Part of** | Learning sketches for [SmartHouse_v1](../README.md#part-2-learning-sketches-inside-this-folder) |

## Notes
🔑 Wi-Fi details are in `arduino_secrets.h` (git-ignored). Copy `arduino_secrets.example.h` to `arduino_secrets.h` on a fresh clone. The comment says "built-in LED", but that is usually GPIO 2.

Serial Monitor: 9600 baud, line ending **Newline**.

## Libraries to install

**Headers included:** `WiFi.h`, `WebServer.h`, `arduino_secrets.h`

1. Install the **esp32 by Espressif Systems** board package (see [LIBRARIES.md → Step 2](../../LIBRARIES.md#step-2-install-the-board-packages)), then select **Tools → Board → esp32 → ESP32 Dev Module**.
2. No extra libraries needed. Everything used is built into the board package.
3. Copy `arduino_secrets.example.h` to `arduino_secrets.h` and fill in your Wi-Fi name and password.
4. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../../LIBRARIES.md).
