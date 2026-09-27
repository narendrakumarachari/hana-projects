# Hana Programs

<!-- circuit-card --> 🔌 **Circuit cards for the Python programs:** https://narendrakumarachari.github.io/hana-projects/

Hana's Python programs, written **July to September 2026**. They go from the very first `print("Hello py")` to **ChirpQuest**, a full kids' bird-guide web app with an AI chatbot. Along the way are PC programs that talk to Arduino and ESP32 boards over USB and Wi-Fi.

> **Board side:** the Arduino / ESP32 sketches these programs talk to are in [`../arduino`](../arduino/README.md).
>
> **Note:** everything here runs on the **PC** with normal Python 3 (CPython). None of it is MicroPython running on the ESP32 itself. The ESP32/Arduino side is written in Arduino C++.

## Folder layout
```
HanaProjects/python/
├── README.md                     ← you are here: index of every program
├── TODO.md                       ← open to-dos from the code review
├── requirements.txt              ← all packages:  pip install -r requirements.txt
├── python-cpp.agent.md           ← custom AI coding-assistant profile (Python + C++)
├── 01_Python_Basics/             ← 13 numbered lessons (run in the terminal)
├── 02_Mini_Projects/             ← Rose Library, Pet Care Agent
├── 03_Arduino_ESP32_Companions/  ← PC programs that control Arduino / ESP32 boards
├── 04_ChirpQuest/                ← the bird-guide web app (+ old versions)
└── venv/                         ← Python virtual environment (not uploaded)
```

## First-time setup (Windows)
```bat
cd C:\Users\narendra\HanaProjects\python
python -m venv venv                  :: only if venv\ doesn't exist yet
venv\Scripts\activate
pip install -r requirements.txt
```
Every time after that, run `venv\Scripts\activate` first, then run programs with `python <file>.py`.

---

## Program index

### 01_Python_Basics: lessons, in the order they were learned
| File | What it teaches / does | Old name |
|---|---|---|
| [01_hello_print.py](01_Python_Basics/01_hello_print.py) | `print()`: the first program | `basics.py` |
| [02_variables.py](01_Python_Basics/02_variables.py) | Variables: "My favorite animal is a Bird" | `Variable.py` |
| [03_input_greeting.py](01_Python_Basics/03_input_greeting.py) | `input()`: asks your name and says hello | `takingiput.py` |
| [04_if_elif_else.py](01_Python_Basics/04_if_elif_else.py) | `if / elif / else` with yes / no / maybe | `ifelifelse.py` |
| [05_calculator.py](01_Python_Basics/05_calculator.py) | Calculator: two numbers and `+ - * /` | `calculator.py` |
| [06_string_indexing.py](01_Python_Basics/06_string_indexing.py) | String indexing `text[0]`, negative indexes, simple slices | `Indexing.py` |
| [07_friendly_chat.py](01_Python_Basics/07_friendly_chat.py) | Chat program: name + "are you friendly?" | `Hello.py` |
| [08_compare_numbers.py](01_Python_Basics/08_compare_numbers.py) | Comparisons and f-strings: which number is bigger | `booleans.py` |
| [09_string_slicing.py](01_Python_Basics/09_string_slicing.py) | String slicing `[start:stop:step]`, step and reverse `[::-1]` (plus a long commented-out "TAMILNADU" reference guide) | `slicing.py` |
| [10_loops.py](01_Python_Basics/10_loops.py) | `for` / `while` / `range()` / `break` notes and a mini game (all commented out) | `loop.py` |
| [11_functions_pet_agents.py](01_Python_Basics/11_functions_pet_agents.py) | Functions: pick 1–4 for a Cat/Fish/Dog/Bird care agent | `functions.py` |
| [12_data_types.py](01_Python_Basics/12_data_types.py) | str / int / float / bool / list / tuple / dict / set, mutable vs immutable | `Datatypes.py` |
| [13_try_except.py](01_Python_Basics/13_try_except.py) | Error handling with `try / except` | `trycatch.py` |

### 02_Mini_Projects
| Project | What it does | Files (old name) |
|---|---|---|
| [RoseLibrary](02_Mini_Projects/RoseLibrary) | "Welcome to Rose Library": log in with a member ID (5 tries), then check out books from the catalogue until you type `done` | `library_checkout.py` (`megaprogect.py`), `books.py` (`megaprobook.py`) |
| [PetCareAgent](02_Mini_Projects/PetCareAgent) | "Call" the pet clinic (number `123 4567`), then talk to a Cat / Dog / Fish / Bird care agent or ask about opening hours, walk-ins and checkup slots | `pet_care_agent_v1.py` (`vetagent1.py`), `pet_care_agent_v2.py` (`vetagent.py`) |

### 03_Arduino_ESP32_Companions: PC programs that control boards
| File | What it does | Talks to | Link | Old name |
|---|---|---|---|---|
| [serial_button_to_keypress.py](03_Arduino_ESP32_Companions/serial_button_to_keypress.py) | When the Arduino button is pressed, types `=` on the PC keyboard | Arduino sketch `Input_Button_SerialEvent` | USB serial COM5, 9600 | `agent.py` |
| [serial_clock_sender.py](03_Arduino_ESP32_Companions/serial_clock_sender.py) | Sends the PC's time and date to an Arduino every second (`HH:MM:SS\|DD\|MM\|YYYY\|DOW`) | an Arduino clock sketch (**not found**, see TODO) | USB serial COM5, 115200 | `clock.py` |
| [serial_sensor_reader.py](03_Arduino_ESP32_Companions/serial_sensor_reader.py) | Reads `Temperature:…,Humidity:…` lines from an Arduino (a tutorial; the whole file is commented out) | an Arduino DHT sketch (**not found**) | USB serial COM5, 115200 | `serialreads.py` |
| [web_led_brightness_slider.py](03_Arduino_ESP32_Companions/web_led_brightness_slider.py) | Web page with a 0–255 slider that sets an LED's brightness on pin 11 | an Arduino PWM sketch (**not found**) | Flask :5000 → USB serial COM5, 9600 | `inoledblink.py` |
| [web_esp32_led_control.py](03_Arduino_ESP32_Companions/web_esp32_led_control.py) | Web page with ON / OFF / BIRD (keep blinking) buttons that control the ESP32's LED over Wi-Fi | Arduino sketch `ESP32_WiFi_LED_WebAPI` | Flask :5000 → HTTP to `192.168.1.248` | `wificomunication.py` |
| [web_tft_animation_noticeboard.py](03_Arduino_ESP32_Companions/web_tft_animation_noticeboard.py) | "TFT Display Controller": pick 1 of 5 screen animations, or send a text notice to the display | a TFT display sketch (**not found**) | Flask :5000 → USB serial COM5, 115200 | `animation.py` |

### 04_ChirpQuest: bird-guide web app ⭐
| File | What it is | Old name |
|---|---|---|
| [chirpquest.py](04_ChirpQuest/chirpquest.py) | **Current version.** Kids' guide to 16 North Texas birds, with "Pip the Cockatiel" AI chat (Google Gemini), real photos, a checklist, videos and badges | `Chirpquestbrd.py` |
| [old_versions/chirpquest_v2_demo.py](04_ChirpQuest/old_versions/chirpquest_v2_demo.py) | Previous version (Sep 5, evening) | `demo chirpquest.py` |
| [old_versions/chirpquest_v1.py](04_ChirpQuest/old_versions/chirpquest_v1.py) | First version (Aug 27) | `app.py` |

Details: [04_ChirpQuest/README.md](04_ChirpQuest/README.md).

### Other
| File | What it is |
|---|---|
| [python-cpp.agent.md](python-cpp.agent.md) | A custom-agent profile for an AI coding assistant (e.g. VS Code Copilot Chat), specialised for Python and C++. Most tools only pick these up from a `.github/agents/` folder, so move it there if you want it active |

---

## Changes made on 2026-09-26 (review and clean-up)
- **Renamed and sorted** every program into the 4 folders above. The old names are in the tables.
- **API keys removed from the code.** All three ChirpQuest files had a Gemini key written in them. They now read it from `04_ChirpQuest/.env`, which is git-ignored. `.env.example` is the template.
- **Deleted `dotenv.py`.** It was an empty file with the same name as the `python-dotenv` library, so Python imported it instead of the real library.
- **Deleted `vetagent copy.py`**, an exact duplicate of `vetagent1.py` (now `pet_care_agent_v1.py`).
- `library_checkout.py` now imports `from books import books`, to match the renamed book list.
- Added `requirements.txt`, `.env.example`, this README and `TODO.md`.
- Moved from `C:\Users\narendra\Hanaprograms` into the combined `HanaProjects` repo (a fresh `venv` was created here).

## GitHub
This folder is part of the **hana-projects** repository (<https://github.com/narendrakumarachari/hana-projects>). How to save new work to GitHub is in the [main README](../README.md#saving-new-work-to-github).

### Using it on another PC
After cloning the repo (see the main README):
```bat
cd hana-projects\python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy 04_ChirpQuest\.env.example 04_ChirpQuest\.env     :: then paste the Gemini key
```
