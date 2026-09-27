# SmartHouse_v1: Smart House (working version 1)

<!-- circuit-card --> 🔌 **Circuit card:** [wiring picture, parts, and step-by-step checklist](https://narendrakumarachari.github.io/hana-projects/cards/smart-house.html)

> A model smart house run by one Arduino Uno. It has an automatic door, a temperature display, a night light, a party mode with music and lights, a bedtime routine with an intruder alarm, and a mini LCD game, all switched by typing commands in the Serial Monitor.
>
> This folder also holds **22 small learning sketches** (June to August 2026), the building blocks that led up to it.

| | |
|---|---|
| **Old name** | `Smarthousev1wrking` ("v1 working") |
| **Board** | Arduino Uno |
| **Libraries** | **LiquidCrystal_I2C** 1.1.2, **Servo** 1.3.0 (installed 2026-09-26), **DHT sensor library** 1.4.7 (+ **Adafruit Unified Sensor**), Wire |
| **Last edited** | 2026-09-26 |

---

## Part 1: The main sketch `SmartHouse_v1.ino`

### Modes (type the command in the Serial Monitor, 9600 baud, Newline)
| Command | What happens |
|---|---|
| `help` | Lists all commands |
| `normal` | **Normal mode** (default at power-up). LCD line 1: `Temp: xx.xC`. Line 2: `Person: N cm` if someone is ≤ 4 cm from the door sensor, otherwise `No person`. The **door opens** (servo 90° for 2.5 s, `Welcome` on the LCD) when a person is there **and** the button is pressed. The **night light** "breathes" (fades up and down) when the LDR reads < 500 (dark). Switching from bedtime to normal plays a "Good morning" tune with yellow light |
| `party` | **Party mode**: RGB LED steps red → green → blue every 200 ms. The passive buzzer plays songs in the background. The **button** changes song: *Super Mario theme → Imperial March → Ode to Joy* |
| `bedtime` | **Bedtime**: lights off, `Good night` on the LCD, and a lullaby plays for 12 s. Then the LCD backlight turns off. **Intruder alarm** stays armed: if anything comes ≤ 4 cm from the sensor, the LCD shows `INTRUDER!` and a red/blue siren runs until it moves away (> 6 cm) |
| `gamemode` | **Chrome Birdie**: a bird on the LCD must jump over clouds. Press the door button to jump. It scores +1 per cloud and restarts after a crash |
| `lock` | Door locked: the button no longer opens it |
| `unlock` | Door works normally again |

### Parts
- Arduino Uno + breadboard
- 16×2 LCD with I2C backpack (0x27)
- DHT11 temperature/humidity sensor
- HC-SR04 ultrasonic sensor (the "doorbell / person" sensor)
- SG90 servo (the door)
- LDR + 10 kΩ divider
- LED + 220 Ω (night light)
- RGB LED + 3 × 220 Ω
- 1 × **passive** buzzer (music), 1 × **active** buzzer (wired but unused, see notes)
- 1 × push button

### Wiring
| Part | Uno pin |
|---|---|
| Servo signal | D2 |
| HC-SR04 TRIG | D3 |
| HC-SR04 ECHO | D4 |
| Active buzzer + | D5 *(declared, never used)* |
| RGB red / green / blue | D7 / D8 / D9 |
| Passive buzzer + | D10 |
| Night-light LED + | D11 (PWM) |
| Push button | D12 → GND (`INPUT_PULLUP`) |
| LDR divider midpoint | A0 |
| DHT11 data | A3 |
| LCD SDA / SCL | A4 / A5 |

### How the code is organised
- `loop()` → `readSerial()` (commands) → `getDistance()` → the current mode's function.
- Music is **non-blocking**. Melodies are stored as `{note, duration}` pairs in **flash memory** (`PROGMEM`) to save the Uno's 2 KB of RAM, and `playSongBackground()` plays one note at a time using `millis()`.
- Night-light fading and RGB stepping also use `millis()` timers.

### Code review notes
- **Memory:** with Servo installed it builds at **51% flash / 72% RAM** (1,484 of 2,048 bytes). Above ~75% RAM an Uno can crash randomly, so move any new text into `F("...")` or `PROGMEM` before adding features.
- `ACTIVE_BUZZER` (D5) is set up but never used. Either use it for the doorbell or free the pin.
- The "person" threshold is **4 cm**, which is tuned for a small model house. Make it a named constant.
- `dht.readTemperature()` can return `NaN` if the sensor isn't connected, and the LCD then shows `Temp:nanC`. Check with `isnan(temp)`.
- On the Uno, `tone()` uses Timer 2, which also drives PWM on **D3 and D11**. The night light on D11 can glitch while a tone plays. Normal mode calls `noTone()` first, so it works in practice. Keep that in mind if you rearrange pins.
- `intruderAlarm()` loops with `while` + `delay`, so serial commands are ignored while the alarm is sounding.
- The `normal` command block has no `return;` (the others do). That's harmless today, but inconsistent.

### To-do
- [ ] Use or remove the active buzzer on D5.
- [ ] Guard against `NaN` temperature.
- [ ] Optional v2: take commands from the IR remote (codes in `IR_RemoteButtons_LCD`) or from Wi-Fi (`ESP32_WiFi_LED_WebAPI`) instead of the USB cable.

---

## Part 2: Learning sketches inside this folder

These were saved inside the Smart House folder while learning each part. The Arduino IDE ignores sub-folders when building the main sketch, so they don't interfere. Each can be opened on its own (**File → Open → the `.ino` inside the sub-folder**). The date prefix is the day it was written.

| Folder (new name) | Old name | What it does | Wiring |
|---|---|---|---|
| `Jun14a_LCD_I2C_PrintName` | `sketch_jun14a` | Prints a name on line 1 of the I2C LCD | LCD SDA A4, SCL A5 |
| `Jun14b_LED_RGB_FadeEachColor` | `sketch_jun14b` | Fades red, then green, then blue in and out, forever | RGB R9 G10 B11 |
| `Jun14d_LED_Fade_5Times` | `sketch_jun14d` | Fades an LED in and out 5 times (in `setup()`), then stays off | LED D11 |
| `Jun14e_LED_Fade_Forever` | `sketch_jun14e` | Fades an LED in and out forever | LED D10 |
| `Jun15a_LED_RGB_Fade_3Rounds` | `sketch_jun15a` | Like Jun14b, but runs the R-G-B fade 3 times per loop | RGB R9 G10 B11 |
| `Jun16a_Music_HappyBirthday_Serial` | `sketch_jun16a` | Type `happy birthday` to play the song (tighter rhythm than the top-level version) | Passive buzzer D8 |
| `Jun16c_LED_SerialOnOff` | `sketch_jun16c` | Type `ON` / `OFF` to switch the LED | LED D13 |
| `Jun17a_Sound_ClapDetect_Serial` | `sketch_jun17a` | Prints `Clap Detected` when the sound sensor triggers | Sound DO D12 |
| `Jun17b_Sound_ClapDetect_LED` | `sketch_jun17b` | Clap turns the LED on | Sound DO D12, LED D13 |
| `Jun18b_Sound_DoubleClap_Beeps` | `sketch_jun18b` | **Double clap** within 1.5 s → beep-beep-beeeep | Sound D12, LED D13, active buzzer D11 |
| `Jun18d_Sound_DoubleClap_Melody` | `sketch_jun18d` | Double clap → plays a short C-E-G-C melody | Sound D12, LED D13, passive buzzer D11 |
| `Jun18e_Sound_AnalogLevel_Serial` | `sketch_jun18e` | Prints the sound sensor's analog value once a second | Sound AO A0 |
| `Jun19a_Ultrasonic_ObjectRemovedAlarm` | `sketch_jun19a` | Beeps if the object in front moves > 5 cm away (see `Security_ObjectRemovedAlarm`) | TRIG D9, ECHO D10, buzzer D13 |
| `Jun19c_Ultrasonic_Distance_Serial` | `sketch_jun19c` | Prints the distance in cm once a second | TRIG D9, ECHO D10 |
| `Jun22b_LDR_Light_Serial` | `sketch_jun22b` | Prints the raw LDR value once a second (use it to calibrate night lights) | LDR A0 |
| `Jun24a_PIR_Motion_Serial` | `sketch_jun24a` | Prints `Motion Detected!` from a PIR sensor | PIR OUT D5 |
| `Jun26a_Button_Buzzer` | `sketch_jun26a` | Buzzer beeps at 1 kHz while the button is held | Button D13, buzzer D12 |
| `Jun26b_Button_Serial` | `sketch_jun26b` | Prints while the button is held | Button D13 |
| `Jun26c_LED_4Patterns_Button` | `sketch_jun26c` | 10 LEDs with 4 patterns (left→right, right→left, bounce, even/odd flash). The button cycles patterns with a beep. Fully non-blocking | LEDs D2–D11, buzzer D12, button D13 |
| `Jul15b_MPU6050_TiltDirection` | `sketch_jul15b` | Reads the MPU6050 accelerometer directly over I2C and prints `LEFT/RIGHT/UP/DOWN/CENTER` from the tilt (every 2 s) | MPU6050 SDA A4, SCL A5 (address 0x68) |
| `Aug16a_ESP32_WiFi_LED_WebAPI` | `sketch_aug16a` | **ESP32**: Wi-Fi web server with `/on`, `/off`, `/PoP` (blink) for an LED. Earlier version of `ESP32_WiFi_LED_WebAPI`. Wi-Fi details are in `arduino_secrets.h` (see that project's README) | LED GPIO 23 |
| `Door_Servo_UltrasonicAutoOpen` | `servodoor12345678910` | **Automatic door**: a person within 20 cm → 3 beeps, the door opens slowly, waits 5 s, beeps, closes slowly, then waits until the person leaves | Servo D10, TRIG D7, ECHO D6, active buzzer D8 |

### Notes on the learning sketches
- ✅ `Jun14a_LCD_I2C_PrintName` used `lcd.begin()` from a duplicate LCD library. It was fixed to `lcd.init()` on 2026-09-26, and the duplicate library was removed.
- `Jun14a` prints a person's full name. Decide whether you want that in a public repo.
- `Aug16a`'s comment says "ESP32 built-in LED", but it uses GPIO 23. The built-in LED is usually GPIO 2.

### To-do (learning sketches)
- [x] Change `lcd.begin()` → `lcd.init()` in Jun14a, and remove the duplicate LCD library.
- [ ] Optional: move these 22 folders out to a top-level `Learning_Steps/` folder, so the Smart House folder only holds the Smart House.

## Libraries to install

**Headers included:** `Wire.h`, `LiquidCrystal_I2C.h`, `Servo.h`, `DHT.h`, `avr/pgmspace.h`

1. Select **Tools → Board → Arduino AVR Boards → Arduino Uno**.
2. Open **Tools → Manage Libraries…** (Ctrl+Shift+I), search for each library below, check the author, and click **Install**:
   - **LiquidCrystal I2C** by Frank de Brabander (1.1.2)
   - **Servo** by Michael Margolis, Arduino (1.3.0)
   - **DHT sensor library** by Adafruit (1.4.7). Click **Install All** to also get **Adafruit Unified Sensor**
3. Click **Upload** (→).

Full list and troubleshooting: [LIBRARIES.md](../LIBRARIES.md).
