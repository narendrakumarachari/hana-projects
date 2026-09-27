# 03_Arduino_ESP32_Companions

Python programs that run **on the PC** and talk to an **Arduino** (over the USB cable, using `pyserial`) or an **ESP32** (over Wi-Fi, using `requests`). Three of them are small **Flask** web servers, so you can control the board from a browser or phone.

**Setup:** `pip install -r requirements.txt` (from the repo root) installs `pyserial`, `Flask`, `requests` and `keyboard`.

**Before running anything that uses serial:**
- Check the COM port in **Arduino IDE → Tools → Port**. Every program assumes **`COM5`**, so edit the `PORT` / `SERIAL_PORT` line if yours differs.
- **Close the Arduino Serial Monitor.** Only one program can use a COM port at a time.
- The baud rate in the Python file must match `Serial.begin(...)` in the sketch.

The sketches are in [`HanaProjects/arduino`](../../arduino/README.md).

---

| Program | What it does | Board side | Connection |
|---|---|---|---|
| `serial_button_to_keypress.py` *(was `agent.py`)* | Prints every line the Arduino sends. When it receives `=`, it **types `=` on the PC keyboard** (for example into Calculator) | ✅ `Input_Button_SerialEvent` (button on D11 sends `BUTTON_PRESSED` and `=`) | COM5 @ 9600 |
| `serial_clock_sender.py` *(was `clock.py`)* | Sends the PC's time every second as `14:32:07\|11\|08\|2026\|TUE`, so an Arduino can show a clock | ❓ receiving sketch **not found** | COM5 @ 115200 |
| `serial_sensor_reader.py` *(was `serialreads.py`)* | Tutorial: read `Temperature:28.50,Humidity:65.00` lines from an Arduino with a DHT sensor. **Entirely commented out**, so it does nothing when run | ❓ sending sketch **not found** | COM5 @ 115200 |
| `web_led_brightness_slider.py` *(was `inoledblink.py`)* | Web page at `http://<pc-ip>:5000` with a 0–255 slider and OFF / FULL buttons. Each change sends the number plus a newline to the Arduino, which sets the LED on pin 11 with `analogWrite` | ❓ receiving sketch **not found** | Flask :5000 → COM5 @ 9600 |
| `web_esp32_led_control.py` *(was `wificomunication.py`)* | Web page with **ON / OFF / BIRD** buttons. BIRD starts a background thread that blinks the ESP32's LED every second until pressed again | ✅ `ESP32_WiFi_LED_WebAPI` (`/on`, `/off`) | Flask :5000 → HTTP to `192.168.1.248` |
| `web_tft_animation_noticeboard.py` *(was `animation.py`)* | "TFT Display Controller" web page: choose 1 of 5 animations (Bouncing Ball, Starfield Warp, Pulsing Circles, Color Wave, Rotating Square) → sends `ANIM,<n>`; or type a message → sends `NOTICE,<text>` | ❓ receiving TFT sketch **not found** | Flask :5000 → COM5 @ 115200 |

## Review notes
- `web_tft_animation_noticeboard.py` is the most robust: one serial connection opened at start-up, a thread lock so two browser clicks can't collide, auto-reconnect, and `use_reloader=False` (explained in a comment).
- `web_led_brightness_slider.py` opens COM5 **when the file loads**. If the Arduino isn't plugged in, it crashes immediately with a `SerialException`. It also doesn't check that `value` is a number.
- `web_esp32_led_control.py` has the ESP32's IP (`192.168.1.248`) hard-coded. It changes if the router hands out a new address, so check the ESP32's Serial Monitor. A failed `requests.get` (ESP32 off) crashes the blink thread. Add a `timeout=` and `try/except`.
- `serial_button_to_keypress.py`: the `keyboard` package may need the terminal to be **run as administrator** on some PCs.
- `serial_clock_sender.py` has a clear docstring and an efficient once-per-second send.

## To-do
- [ ] Find the 4 missing Arduino sketches (clock display, DHT sender, PWM LED receiver, TFT animation/noticeboard) and add them to `../arduino`, or note here that they were never saved.
- [ ] Put the COM port and ESP32 IP in one settings file (or `.env`) instead of each program.
- [ ] `serial_sensor_reader.py`: un-comment it once the DHT sketch exists.
