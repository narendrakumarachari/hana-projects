# ESP32_WiFi_LED_WebAPI

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/esp32-wifi-led.html)

> ⭐ **Featured project:** this sketch is the board half of **[LED From Anywhere](https://narendrakumarachari.github.io/hana-projects/led-from-anywhere.html)**. With the Python web remote and ngrok, friends anywhere in the world can switch this LED on.
>
> The ESP32 joins your Wi-Fi and runs a tiny web server. Visit `/on`, `/off` or `/bird` in a browser to control an LED.

| | |
|---|---|
| **Old name** | `ESP32_api` |
| **Board** | **ESP32 Dev Module** (esp32 core 3.3.x) |
| **Libraries** | WiFi, WebServer (both come with the ESP32 core) |
| **Last edited** | 2026-08-17 |

## What it does
1. Connects to Wi-Fi and prints dots while it waits, then prints the ESP32's IP address at **9600 baud**.
2. Starts an HTTP server on port 80:

| URL | Action | Reply |
|---|---|---|
| `http://<ip>/on` | LED on | `LED ON` |
| `http://<ip>/off` | LED off | `LED OFF` |
| `http://<ip>/bird` | LED blinks once (0.5 s on, 0.5 s off) | `bird - LED blinked` |

## 🔑 Wi-Fi password setup (do this first)
The Wi-Fi name and password are **not** in the `.ino` file. They are in `arduino_secrets.h`, which is git-ignored so it never reaches GitHub.

1. Copy `arduino_secrets.example.h` to `arduino_secrets.h` (same folder).
2. Put your Wi-Fi name and password in it.
3. Upload.

On a fresh clone from GitHub, only the example file exists. The sketch won't compile until you do step 1.

## Parts
- ESP32 Dev board (the built-in blue LED on GPIO 2 is used)

## Wiring
| Part | ESP32 pin |
|---|---|
| LED (built in) | GPIO 2 |

## How to use
1. Upload, open the Serial Monitor at 9600, and note the IP (e.g. `192.168.1.42`).
2. On a phone or PC **on the same Wi-Fi**, open `http://192.168.1.42/on`.

## Code review notes
- There is no page at `/`, so visiting just the IP gives "Not found". A small HTML page with ON/OFF buttons would be friendlier.
- `/bird` blocks the server for 1 s (`delay`). That's fine for one user.
- If Wi-Fi is wrong, it waits forever printing dots. Add a timeout message.
- Earlier version: `SmartHouse_v1/Aug16a_ESP32_WiFi_LED_WebAPI` (LED on GPIO 23, `/PoP` endpoint).
- The name "bird" hints at a planned link to the bird projects (see `WIP_Bird_Empty`).

## To-do
- [ ] Add a home page (`/`) with buttons.
- [ ] Add a Wi-Fi connect timeout.
- [ ] Optional: use mDNS so it's reachable at `http://esp32.local/`.

## Libraries to install

**Headers included:** `WiFi.h`, `WebServer.h`, `arduino_secrets.h`

1. Install the **esp32 by Espressif Systems** board package (see [LIBRARIES.md → Step 2](../LIBRARIES.md#step-2-install-the-board-packages)), then select **Tools → Board → esp32 → ESP32 Dev Module**.
2. No extra libraries needed. Everything used is built into the board package.
3. Copy `arduino_secrets.example.h` to `arduino_secrets.h` and fill in your Wi-Fi name and password.
4. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
