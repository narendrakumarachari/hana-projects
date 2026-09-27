# LED_Brightness_WebSlider

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/led-brightness-web-slider.html)

> ⭐ **Part of the featured project "LED From Anywhere".** A web-page slider (0–255) sends a number over USB, and the Uno dims the LED to match. Share the page with **ngrok** and friends anywhere in the world can move the slider.

| | |
|---|---|
| **Where it came from** | Shared by the teacher in class on **2026-08-07**. Found in the class chat and added to the repo on 2026-09-26 (it was the missing board half of `web_led_brightness_slider.py`) |
| **Board** | Arduino Uno |
| **Libraries** | none |
| **Python partner** | [`python/03_Arduino_ESP32_Companions/web_led_brightness_slider.py`](../../python/03_Arduino_ESP32_Companions/web_led_brightness_slider.py) |
| **Step-by-step mission** | [LED From Anywhere](https://narendrakumarachari.github.io/hana-projects/led-from-anywhere.html) · [ngrok guide](https://narendrakumarachari.github.io/hana-projects/share-with-ngrok.html) |

## What it does
Waits for a number on the serial port (9600 baud), keeps it between 0 and 255, sets the LED on pin 11 to that brightness with `analogWrite`, and prints the number back.

## Wiring
| Part | Uno pin |
|---|---|
| LED long leg (+), through a 220 Ω resistor | ~11 |
| LED short leg (−) | GND |

## How to use
1. **Test it alone:** open the Serial Monitor at 9600 baud, type `128`, press Enter. The LED glows at half brightness.
2. **Close the Serial Monitor.** The Python program needs the USB port to itself.
3. Run the web page: double-click `python/03_Arduino_ESP32_Companions/DEMO_LED_from_anywhere_Uno_slider.bat`. It starts the slider page **and** ngrok, which prints your world link.

## To-do
- [ ] Optional: add a second LED on pin ~10 and a second slider.
