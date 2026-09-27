# To-do list: Hana Programs

From the code review on **2026-09-26**. Details are in each folder's `README.md`.

## ✅ Done during the clean-up
- [x] Gemini API keys removed from all 3 ChirpQuest files, now in `04_ChirpQuest/.env` (git-ignored)
- [x] Deleted empty `dotenv.py` (it hid the real `python-dotenv` library)
- [x] Deleted `vetagent copy.py` (exact duplicate)
- [x] Renamed every file to a meaningful name and sorted them into 4 folders
- [x] Added `requirements.txt`, `.gitignore`, `.env.example` and READMEs

## 🔴 Important
- [ ] **ChirpQuest**: chat text is inserted as raw HTML. Switch to `textContent` (see `04_ChirpQuest/README.md`).
- [ ] **Gemini keys**: three different keys were written in old files. In Google AI Studio (<https://aistudio.google.com/apikey>), delete the ones you no longer use, and keep only the one in `.env`.
- [ ] **Missing Arduino sketches**: find and save the board-side code for `serial_clock_sender.py`, `serial_sensor_reader.py`, `web_led_brightness_slider.py` and `web_tft_animation_noticeboard.py`.

## 🟠 Bugs to fix (good practice exercises)
- [ ] `05_calculator.py`: divide by zero crashes.
- [ ] `08_compare_numbers.py`: equal numbers print nothing.
- [ ] `13_try_except.py`: a second wrong answer crashes. Loop until the input is valid, and use `except ValueError`.
- [ ] `10_loops.py`: examples print `i` but the loop variable has a different name.
- [ ] `RoseLibrary`: titles must match capitals exactly, and a non-number ID ends the program.
- [ ] `web_led_brightness_slider.py`: crashes at start if the Arduino isn't plugged in.
- [ ] `web_esp32_led_control.py`: the blink thread crashes if the ESP32 is off. Add `timeout=` and `try/except`.

## 🟢 Ideas
- [ ] One `settings` file (or `.env`) for the COM port and ESP32 IP, used by all the companion programs.
- [ ] ChirpQuest: split into `templates/` and `static/`, add more birds and real bird-call recordings.
- [ ] PetCareAgent: store the animal data in JSON, add appointment booking.
- [ ] RoseLibrary: save checked-out books to a file.
- [ ] `python-cpp.agent.md`: move it to `.github/agents/` if you want your AI assistant to pick it up.
