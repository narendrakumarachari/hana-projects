# Hana Projects

[![Build](https://github.com/narendrakumarachari/hana-projects/actions/workflows/build.yml/badge.svg)](https://github.com/narendrakumarachari/hana-projects/actions/workflows/build.yml)

Everything Hana built from **June to September 2026**, in one place:
- **Arduino and ESP32 hardware projects**: LEDs, sensors, alarms, a smart house, LCD and colour-screen games.
- **Python programs**: first lessons, mini projects, PC apps that control the boards, and the **ChirpQuest** bird-guide web app.

## What's inside
```
HanaProjects/                     ← this repo (github.com/narendrakumarachari/hana-projects)
├── README.md                     ← you are here
├── .gitignore                    ← keeps Wi-Fi passwords, API keys and venv/ off GitHub
├── arduino/                      ← Arduino IDE sketchbook: 33 projects + 22 learning sketches
│   ├── README.md                 ← index of every sketch
│   ├── LIBRARIES.md              ← what to install
│   ├── TODO.md
│   ├── libraries/
│   └── SkyGuardTFT/, SmartHouse_v1/, Project_HanaMiniTV_IR_LCD/, …
└── python/                       ← Python 3 programs (run on the PC)
    ├── README.md                 ← index of every program
    ├── TODO.md
    ├── requirements.txt
    ├── 01_Python_Basics/  02_Mini_Projects/
    ├── 03_Arduino_ESP32_Companions/   ← PC apps that talk to the boards
    └── 04_ChirpQuest/
```

| Folder | Start here | Highlights |
|---|---|---|
| [`arduino/`](arduino) | [arduino/README.md](arduino/README.md) | ⭐ [SkyGuardTFT](arduino/SkyGuardTFT) (ESP32 arcade game), [SmartHouse_v1](arduino/SmartHouse_v1), [Hana Mini TV](arduino/Project_HanaMiniTV_IR_LCD) |
| [`python/`](python) | [python/README.md](python/README.md) | ⭐ [ChirpQuest](python/04_ChirpQuest) (bird guide with an AI chatbot), [Pet Care Agent](python/02_Mini_Projects), [board controllers](python/03_Arduino_ESP32_Companions) |

### How the two halves connect
| Python program (PC) | Arduino / ESP32 sketch (board) | Link |
|---|---|---|
| [`serial_button_to_keypress.py`](python/03_Arduino_ESP32_Companions/serial_button_to_keypress.py) | [`Input_Button_SerialEvent`](arduino/Input_Button_SerialEvent) | USB serial |
| [`web_esp32_led_control.py`](python/03_Arduino_ESP32_Companions/web_esp32_led_control.py) | [`ESP32_WiFi_LED_WebAPI`](arduino/ESP32_WiFi_LED_WebAPI) | Wi-Fi (HTTP) |
| clock sender, sensor reader, LED slider, TFT noticeboard | *board sketches not found yet* (see [python/TODO.md](python/TODO.md)) | USB serial |

---

## Setting up on a PC
**Arduino:** install Arduino IDE 2, then **File → Preferences → Sketchbook location** → `C:\Users\narendra\HanaProjects\arduino`. The libraries are already in `arduino/libraries`. Board packages and troubleshooting: [arduino/LIBRARIES.md](arduino/LIBRARIES.md).

**Python:**
```bat
cd C:\Users\narendra\HanaProjects\python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```
For ChirpQuest, also copy `04_ChirpQuest\.env.example` to `04_ChirpQuest\.env` and paste the Gemini key.

---

## Saving new work to GitHub
```bat
cd C:\Users\narendra\HanaProjects
git status                          :: see what changed
git add .
git commit -m "Short description of what you changed"
git push
```
**Always check `git status` before `git add`.** These files must **never** appear in the list: `arduino_secrets.h`, `.env`, `venv\`.

### Automatic checks (GitHub Actions)
Every push runs [`.github/workflows/build.yml`](.github/workflows/build.yml) on GitHub. The badge at the top turns ✅ green or ❌ red, and the details are on the repo's **Actions** tab.

| Job | What it checks |
|---|---|
| **Arduino (uno)** | compiles every Uno sketch with the libraries in `arduino/libraries` |
| **Arduino (esp32)** | compiles every ESP32 sketch (Wi-Fi sketches use their `arduino_secrets.example.h`) |
| **Python** | installs `requirements.txt`, checks every `.py` file for syntax errors, and starts ChirpQuest to test its pages (no API key needed) |

- The compile list is in [`.github/scripts/compile_sketches.sh`](.github/scripts/compile_sketches.sh). New sketches are picked up automatically. A folder name starting with `ESP32_` (or listed in `board_for`) is built for the ESP32; everything else for the Uno.
- `WIP_Bird_Empty` is skipped until it has code. Remove it from `SKIP` in the script once it does.
- To re-run by hand: **Actions → Build → Run workflow**.

### Getting the repo on a new PC
```bat
git clone https://github.com/narendrakumarachari/hana-projects.git C:\Users\narendra\HanaProjects
```
Then follow **Setting up on a PC** above, and recreate the secret files from their `.example` templates:
- `arduino/ESP32_WiFi_LED_WebAPI/arduino_secrets.h`
- `arduino/SmartHouse_v1/Aug16a_ESP32_WiFi_LED_WebAPI/arduino_secrets.h`
- `python/04_ChirpQuest/.env`

---

## History
- **2026-06 → 09:** projects written in `Documents\Arduino` and `C:\Users\narendra\Hanaprograms`.
- **2026-09-26:** reviewed, renamed, documented, secrets moved out of the code, and combined into this repo.
