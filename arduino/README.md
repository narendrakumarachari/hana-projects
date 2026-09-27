# Arduino & ESP32 Projects

<!-- circuit-card --> 🔌 **Circuit cards for every sketch:** https://narendrakumarachari.github.io/hana-projects/

## Folder layout
```
HanaProjects/arduino/     ← the Arduino IDE sketchbook folder
├── README.md             ← you are here: index of every sketch
├── LIBRARIES.md          ← what to install for each project
├── TODO.md               ← all open to-dos
├── libraries/            ← Arduino libraries (must stay here for the IDE)
└── <33 sketch folders>   ← listed below
```
- **New Arduino project:** a new folder here (folder name = `.ino` name).
- **Arduino IDE setting:** File → Preferences → *Sketchbook location* = `C:\Users\narendra\HanaProjects\arduino`.
- **Python side:** Hana's Python programs, including the PC apps that control these boards, are in [`../python`](../python/README.md).

---

## Arduino & ESP32 projects

A collection of **55 Arduino sketches** (33 projects + 22 learning steps) written between **June and September 2026**. It starts with blinking LEDs and ends with a full-colour ESP32 arcade game. Each project folder has its own `README.md` with the parts list, a wiring table, how to use it, code-review notes and a to-do list.

> **Coming back after a long time? Start here.**
> 1. Find the project in the index below (the names say what they do).
> 2. Open its folder's `README.md` for wiring and usage.
> 3. Set up the IDE and libraries with [LIBRARIES.md](LIBRARIES.md).
> 4. See what's unfinished in [TODO.md](TODO.md).

---

## Naming scheme
Every folder is named `Category_WhatItDoes_KeyPart`, so the list sorts by category.

| Prefix | Meaning |
|---|---|
| `Basics_` | first-test sketches |
| `LED_` | LED effects |
| `Music_` / `Sound_` | buzzer melodies / sound sensors and bird sounds |
| `Sensor_` | one sensor driving an output |
| `Security_` | alarms |
| `Door_` | servo doors |
| `IR_` | infrared remote |
| `LCD_` / `Display_` | 16×2 LCD / LED matrix |
| `Input_` | buttons |
| `Game_` | games |
| `Project_` | bigger multi-feature builds |
| `ESP32_` | Wi-Fi projects on the ESP32 |
| `Tool_` | debugging utilities |
| `WIP_` | started, not finished |

Arduino requires the folder and the `.ino` file inside it to have **the same name**. They were renamed together. The old → new names are in the last column of each table.

---

## Project index

**Build** = result of compiling every sketch with `arduino-cli` on 2026-09-26: ✅ builds, ⚠️ needs a fix (see note), ❌ empty.
**Board**: **Uno** = Arduino Uno (ATmega328P), **ESP32** = ESP32 Dev Module.

### ⭐ Main projects
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [SkyGuardTFT](SkyGuardTFT) | Eagle-vs-bugs arcade game on a 240×240 colour TFT: 4 weapons, talon flip, saved best score | ESP32 | ✅ | `SkyGuardTFT` |
| [SmartHouse_v1](SmartHouse_v1) | Model smart house: auto door, temperature, night light, party/bedtime/game modes, intruder alarm, plus 22 learning sketches | Uno | ✅ | `Smarthousev1wrking` |
| [Project_HanaMiniTV_IR_LCD](Project_HanaMiniTV_IR_LCD) | "Hana TV": 9 animated channels and mini-games on a 16×2 LCD, controlled by an IR remote | Uno | ✅ | `minitv1245` |

### Basics & LEDs
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Basics_HelloWorld_Serial](Basics_HelloWorld_Serial) | Prints "Hello World" every 5 s | Uno | ✅ | `HelloWorld` |
| [LED_RGB_ColorCycle](LED_RGB_ColorCycle) | RGB LED: red → green → blue | Uno | ✅ | `TR5` |
| [LED_Scanner_Buzzer](LED_Scanner_Buzzer) | Knight-Rider sweep on 10 LEDs, with a note per LED | Uno | ✅ | `ledunison353` |
| [LED_Scanner_DualBuzzer_Show](LED_Scanner_DualBuzzer_Show) | 4-act LED + sound show (2nd buzzer silent, see README) | Uno | ✅ | `ledunison123` |

### Music & sound
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Music_HappyBirthday_Serial](Music_HappyBirthday_Serial) | Type "happy birthday" → buzzer plays it | Uno | ✅ | `Birthday2` |
| [Music_HappyBirthday_LEDShow](Music_HappyBirthday_LEDShow) | Krish's birthday: song + 10-LED dance + celebration | Uno | ✅ | `krishbdaytreat454` |
| [Sound_RandomBirdChirps](Sound_RandomBirdChirps) | Natural random bird chirps from 2 buzzers | Uno | ✅ | `birdcalllllls22346454` |
| [Sound_BirdPiano_5Buttons](Sound_BirdPiano_5Buttons) | Krish's bird "piano": 5 buttons = 5 sparrow calls (Food, Water, Play, Scritches, Outside) | Uno | ✅ | `birdpiano2345432` |
| [Sound_ClapDetect_LED_Buzzer](Sound_ClapDetect_LED_Buzzer) | Clap → LED + beep | Uno | ✅ | `save3` |
| [Sound_ClapSensor_MarioMelody](Sound_ClapSensor_MarioMelody) | Sound sensor starts/stops the Mario theme | Uno | ✅ | `buzz6796` |
| [Sound_LoudnessAlarm_Analog](Sound_LoudnessAlarm_Analog) | Beeps when the analog sound level ≥ 625 | Uno | ✅ | `soundtime55fun` |

### Sensors & security
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Sensor_AutoNightLight_LDR](Sensor_AutoNightLight_LDR) | LED full / half / off based on light level | Uno | ✅ | `nightligt6700` |
| [Sensor_ParkingSensor_Ultrasonic](Sensor_ParkingSensor_Ultrasonic) | Beeps faster as an object gets closer | Uno | ✅ | `car33` |
| [Security_ObjectRemovedAlarm](Security_ObjectRemovedAlarm) | Alarm when an object is lifted away from the sensor | Uno | ✅ | `steal777` |
| [Security_NightTheftAlarm](Security_NightTheftAlarm) | Street light + object alarm armed only at night | Uno | ✅ | `seal888` |
| [Security_TheftDetector_PoliceSiren](Security_TheftDetector_PoliceSiren) | Final version: night guard + red/blue police siren | Uno | ✅ | `final12345` |

### Doors, IR remote, displays, input
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Door_Servo_ButtonOpen](Door_Servo_ButtonOpen) | Button → servo door opens 5 s | Uno | ✅ | `Sweep` |
| [Door_RFID_AccessControl](Door_RFID_AccessControl) | RFID card unlocks the servo door | Uno | ✅ | `entercard12345` |
| [IR_RemoteCodeReader](IR_RemoteCodeReader) | Prints the hex code of any IR button | Uno | ✅ | `IRHEX123` |
| [IR_RemoteButtons_LCD](IR_RemoteButtons_LCD) | Shows the IR button name on the LCD, **plus the full remote code table** | Uno | ✅ | `remoteHEXir34` |
| [LCD_SerialMessageBoard](LCD_SerialMessageBoard) | Type in the Serial Monitor → shows on the LCD | Uno | ✅ | `LCDMSG25434` |
| [Display_LEDMatrix_LetterK](Display_LEDMatrix_LetterK) | Letter "K" on an 8×8 MAX7219 matrix | Uno | ✅ | `matrix15678423` |
| [Input_Button_SerialEvent](Input_Button_SerialEvent) | Debounced button → sends `BUTTON_PRESSED` to the PC | Uno | ✅ | `keyboard2345` |

### Games
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Game_SkyGuardian_LCD](Game_SkyGuardian_LCD) | First Sky Guard: eagle vs bugs on a 16×2 LCD | Uno | ✅ | `skyguard13455` |
| [Game_FlappyBird_LCD](Game_FlappyBird_LCD) | Flappy Bird on a 16×2 LCD (flicker-free) | Uno | ✅ | `flappybird0000` |
| [SkyGuardTFT](SkyGuardTFT) | *(see Main projects)* | ESP32 | ✅ | — |

### ESP32 Wi-Fi
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [ESP32_WiFi_LED_WebAPI](ESP32_WiFi_LED_WebAPI) | Web server: `/on`, `/off`, `/bird` control an LED | ESP32 | ✅ | `ESP32_api` |

### Tools
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [Tool_I2C_Scanner](Tool_I2C_Scanner) | Lists all I2C device addresses | Uno | ✅ | `i2cfind3456` |
| [Tool_ST7789_WiringFinder](Tool_ST7789_WiringFinder) | Tries common TFT wire mix-ups to find which one works | ESP32 | ✅ | `TFTTest` |
| [Tool_ST7789_HealthCheck](Tool_ST7789_HealthCheck) | Is the TFT dead? Wire short test + chip ID + colour test | ESP32 | ✅ | `TFTCheck` |

### Work in progress
| Project | What it does | Board | Build | Old name |
|---|---|---|---|---|
| [WIP_Bird_Empty](WIP_Bird_Empty) | Empty placeholder (0-byte file) | — | ❌ empty | `Bird.sep26` |

### Learning sketches (inside `SmartHouse_v1/`)
22 small step-by-step sketches: LED fades, clap detection, ultrasonic, LDR, PIR, buttons, MPU6050 tilt, an ESP32 web LED and an ultrasonic auto-door. The full table is in [SmartHouse_v1/README.md](SmartHouse_v1/README.md#part-2-learning-sketches-inside-this-folder). All build except `Jun14a_LCD_I2C_PrintName` (one-line fix).

---

## How the projects grew (the story)
1. **June 14–16**: LEDs, RGB fades, the I2C LCD, and Happy Birthday on a buzzer, triggered from the Serial Monitor.
2. **June 17–19**: sound sensor (clap, double clap), ultrasonic distance → parking sensor, and the object-removed alarm.
3. **June 19–23**: LDR night light → night-time theft alarm → **police-siren theft detector**.
4. **June 24–30**: PIR, buttons, the 10-LED scanner shows, Krish's birthday light show, bird chirps, the **bird piano**, the servo door, the LED matrix.
5. **July**: I2C scanner, MPU6050 tilt, **Flappy Bird** and **Sky Guardian** on the LCD, the RFID door, IR remote decoding.
6. **Late July**: **Hana Mini TV**, which combines the IR remote, LCD animations and games.
7. **August**: first **ESP32** Wi-Fi web server.
8. **September**: **Smart House v1** finished; **SkyGuard TFT** on the ESP32 with a colour screen, plus TFT debugging tools.

---

## Hardware used across all projects
| Part | Used in |
|---|---|
| Arduino Uno | almost everything |
| ESP32 Dev Module (CH340/CP2102 USB) | SkyGuardTFT, ESP32_WiFi_LED_WebAPI, Aug16a, Tool_ST7789_* |
| 1.54" 240×240 ST7789 SPI TFT | SkyGuardTFT, Tool_ST7789_* |
| 16×2 LCD + I2C backpack (0x27) | LCD/IR/Game/MiniTV/SmartHouse |
| MAX7219 8×8 LED matrix | Display_LEDMatrix_LetterK |
| LEDs (×10), RGB LED, 220 Ω resistors | LED_*, Music_*, Security_* |
| Passive buzzer (plays notes) | Music_*, Sound_*, games |
| Active buzzer (one beep tone) | clap sketches, alarms, parking sensor |
| Sound sensor module (DO + AO) | Sound_* |
| HC-SR04 ultrasonic | Sensor_Parking, Security_*, Door_Servo_UltrasonicAutoOpen, SmartHouse |
| LDR + 10 kΩ | Sensor_AutoNightLight, Security_*, SmartHouse |
| PIR motion sensor | SmartHouse/Jun24a |
| DHT11 temperature sensor | SmartHouse |
| MPU6050 accelerometer | SmartHouse/Jul15b |
| SG90 servo | Door_*, SmartHouse |
| RC522 RFID reader + cards | Door_RFID_AccessControl |
| IR receiver (VS1838B) + 21-key remote | IR_*, Project_HanaMiniTV |
| Analog joystick | Game_* , SkyGuardTFT |
| Push buttons | many |

### Common things to remember
- **Serial Monitor speed**: Uno sketches use **9600** baud. SkyGuardTFT and the TFT tools use **115200**. When sending commands, set the line ending to **Newline**.
- **Passive vs active buzzer**: a passive buzzer needs `tone()` and can play melodies. An active buzzer just beeps when given power.
- **Only one `tone()` at a time** on an Uno. A second buzzer can't play at the same moment.
- **LCD blank?** Run `Tool_I2C_Scanner`. The address is 0x27 or 0x3F. Then turn the contrast screw on the back.
- **ESP32 pins are 3.3V.** Never feed 5V into them (for example, from a joystick powered at 5V).
- **Uno I2C pins** are A4 (SDA) and A5 (SCL).

---

## GitHub
This folder is part of the **hana-projects** repository (<https://github.com/narendrakumarachari/hana-projects>). How to save new work to GitHub is in the [main README](../README.md#saving-new-work-to-github).

### Privacy
- Wi-Fi password: ✅ kept out of the code, in git-ignored `arduino_secrets.h`.
- Names in the code ("Krish", "Hana", and a full name in `Jun14a`): kept, by choice.
- RFID card UID in `Door_RFID_AccessControl`: harmless for a toy door.
