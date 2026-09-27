# Libraries & setup: what to install to run each project

This list was produced by **scanning every `#include` in every sketch**, then compiling each one with `arduino-cli` and recording the libraries the compiler actually used, including hidden dependencies. Checked on **2026-09-26**.

> The `libraries/` folder is uploaded with the repo, so a copy of every library is here too. If the Arduino IDE's **sketchbook location** is set to this `arduino` folder (File → Preferences), the IDE picks them up automatically and you can skip step 3. On a new PC, either clone the repo and set that sketchbook location, or follow the steps below.

---

## Step 1: Install the Arduino IDE
Download **Arduino IDE 2.x** from <https://www.arduino.cc/en/software> and install it.

## Step 2: Install the board packages
| Board | Package (Boards Manager) | Version used | Needed by |
|---|---|---|---|
| Arduino Uno | **Arduino AVR Boards** by Arduino | 1.8.8 | every Uno sketch (usually pre-installed) |
| ESP32 Dev Module | **esp32** by Espressif Systems | 3.3.11 | SkyGuardTFT, ESP32_WiFi_LED_WebAPI, SmartHouse_v1/Aug16a_…, Tool_ST7789_WiringFinder, Tool_ST7789_HealthCheck |

**How to install the ESP32 package:**
1. **File → Preferences → Additional boards manager URLs**, paste
   `https://espressif.github.io/arduino-esp32/package_esp32_index.json` and click OK.
2. **Tools → Board → Boards Manager…**, search **esp32**, and click **Install** on "esp32 by Espressif Systems".
3. Select **Tools → Board → esp32 → ESP32 Dev Module**.
4. If no COM port appears when the ESP32 is plugged in, install its USB driver: **CH340** (square chip) or **CP210x** (small chip marked "SiLabs").

## Step 3: Install the libraries (Library Manager)
**How to install any library:**
1. **Tools → Manage Libraries…** (or the 📚 icon on the left, or **Ctrl+Shift+I**).
2. Type the name in the search box.
3. Find the entry by the **exact author** shown below (several libraries have similar names).
4. Pick the version (optional) and click **Install**.
5. If a pop-up asks to install dependencies, click **Install All**.

### The 10 libraries to install
| # | Search for | Pick the one by | Version | Header it provides | Extra dependencies |
|---|---|---|---|---|---|
| 1 | `LiquidCrystal I2C` | **Frank de Brabander** | 1.1.2 | `LiquidCrystal_I2C.h` | — |
| 2 | `IRremote` | **shirriff, z3t0, ArminJo** | 4.7.1 (must be **4.x**) | `IRremote.hpp` | — |
| 3 | `Servo` | **Michael Margolis, Arduino** | 1.3.0 | `Servo.h` | — |
| 4 | `MFRC522` | **GithubCommunity** (miguelbalboa) | 1.4.12 | `MFRC522.h` | — |
| 5 | `DHT sensor library` | **Adafruit** | 1.4.7 | `DHT.h` | → #6 (click **Install All**) |
| 6 | `Adafruit Unified Sensor` | **Adafruit** | 1.1.15 | `Adafruit_Sensor.h` | installed with #5 |
| 7 | `LedControl` | **Eberhard Fahle** | 1.0.6 | `LedControl.h` | — |
| 8 | `Adafruit ST7735 and ST7789 Library` | **Adafruit** | 1.11.0 | `Adafruit_ST7789.h` | → #9, #10 (click **Install All**) |
| 9 | `Adafruit GFX Library` | **Adafruit** | 1.12.6 | `Adafruit_GFX.h` | → #10 |
| 10 | `Adafruit BusIO` | **Adafruit** | 1.17.4 | (used inside GFX) | installed with #8/#9 |

**Shortcut:** install **#1, #2, #3, #4, #5, #7, #8**, clicking **Install All** each time. The other three come along automatically.

**Or from the command line** (the same `arduino-cli` that ships inside the IDE):
```bat
"C:\Program Files\Arduino IDE\resources\app\lib\backend\resources\arduino-cli.exe" lib install "LiquidCrystal I2C@1.1.2" "IRremote@4.7.1" "Servo@1.3.0" "MFRC522@1.4.12" "DHT sensor library@1.4.7" "Adafruit Unified Sensor@1.1.15" "LedControl@1.0.6" "Adafruit ST7735 and ST7789 Library@1.11.0" "Adafruit GFX Library@1.12.6" "Adafruit BusIO@1.17.4"
```

### Built in: nothing to install
| Header | Comes with |
|---|---|
| `Wire.h`, `SPI.h`, `avr/pgmspace.h`, `Arduino.h` | the board package (AVR or ESP32) |
| `WiFi.h`, `WebServer.h`, `Preferences.h` | the **esp32** board package only (they will *not* work on an Uno) |

### Files inside the project folders (no install, but read this)
| File | Project | What to do |
|---|---|---|
| `GameTypes.h`, `Sprites.h` | SkyGuardTFT | Already in the folder. Keep them next to `SkyGuardTFT.ino` (they show as tabs in the IDE) |
| `arduino_secrets.h` | ESP32_WiFi_LED_WebAPI, SmartHouse_v1/Aug16a_… | **Not in the repo** (it holds the Wi-Fi password). Copy `arduino_secrets.example.h` → `arduino_secrets.h` and type in your Wi-Fi name and password |

---

## Per-project requirements
Uno = select **Tools → Board → Arduino AVR Boards → Arduino Uno**. ESP32 = **ESP32 Dev Module**.

### No libraries needed (just select the board and upload)
Basics_HelloWorld_Serial · LED_RGB_ColorCycle · LED_Scanner_Buzzer · LED_Scanner_DualBuzzer_Show · Music_HappyBirthday_Serial · Music_HappyBirthday_LEDShow · Sound_RandomBirdChirps · Sound_BirdPiano_5Buttons · Sound_ClapDetect_LED_Buzzer · Sound_ClapSensor_MarioMelody · Sound_LoudnessAlarm_Analog · Sensor_AutoNightLight_LDR · Sensor_ParkingSensor_Ultrasonic · Security_ObjectRemovedAlarm · Security_NightTheftAlarm · Security_TheftDetector_PoliceSiren · Input_Button_SerialEvent · Tool_I2C_Scanner *(uses built-in Wire)* · WIP_Bird_Empty *(empty)*
and learning sketches Jun14b, Jun14d, Jun14e, Jun15a, Jun16a, Jun16c, Jun17a, Jun17b, Jun18b, Jun18d, Jun18e, Jun19a, Jun19c, Jun22b, Jun24a, Jun26a, Jun26b, Jun26c, Jul15b *(uses built-in Wire)*.
All on **Uno**.

### Projects that need libraries
| Project | Board | Install these (numbers from the table above) | Included headers |
|---|---|---|---|
| **SmartHouse_v1** | Uno | #1 LiquidCrystal I2C, #3 Servo, #5 DHT sensor library (+ #6 Unified Sensor) | `Wire.h` `LiquidCrystal_I2C.h` `Servo.h` `DHT.h` `avr/pgmspace.h` |
| **SkyGuardTFT** | ESP32 | ESP32 board package, #8 ST7735/ST7789 (+ #9 GFX, #10 BusIO) | `Adafruit_GFX.h` `Adafruit_ST7789.h` `SPI.h` `Preferences.h` `GameTypes.h` `Sprites.h` |
| **Project_HanaMiniTV_IR_LCD** | Uno | #1 LiquidCrystal I2C, #2 IRremote | `Wire.h` `LiquidCrystal_I2C.h` `IRremote.hpp` |
| Door_Servo_ButtonOpen | Uno | #3 Servo | `Servo.h` |
| Door_RFID_AccessControl | Uno | #3 Servo, #4 MFRC522 | `SPI.h` `MFRC522.h` `Servo.h` |
| IR_RemoteCodeReader | Uno | #2 IRremote | `IRremote.hpp` |
| IR_RemoteButtons_LCD | Uno | #1 LiquidCrystal I2C, #2 IRremote | `Wire.h` `LiquidCrystal_I2C.h` `IRremote.hpp` |
| LCD_SerialMessageBoard | Uno | #1 LiquidCrystal I2C | `Wire.h` `LiquidCrystal_I2C.h` |
| Display_LEDMatrix_LetterK | Uno | #7 LedControl | `LedControl.h` |
| Game_SkyGuardian_LCD | Uno | #1 LiquidCrystal I2C | `Wire.h` `LiquidCrystal_I2C.h` |
| Game_FlappyBird_LCD | Uno | #1 LiquidCrystal I2C | `Wire.h` `LiquidCrystal_I2C.h` |
| ESP32_WiFi_LED_WebAPI | ESP32 | ESP32 board package + create `arduino_secrets.h` | `WiFi.h` `WebServer.h` `arduino_secrets.h` |
| Tool_ST7789_WiringFinder | ESP32 | ESP32 board package, #8 (+ #9, #10) | `Adafruit_GFX.h` `Adafruit_ST7789.h` `SPI.h` |
| Tool_ST7789_HealthCheck | ESP32 | ESP32 board package, #8 (+ #9, #10) | `Adafruit_GFX.h` `Adafruit_ST7789.h` `SPI.h` |
| SmartHouse_v1/Jun14a_LCD_I2C_PrintName | Uno | #1 LiquidCrystal I2C **and** change `lcd.begin()` → `lcd.init()` (see conflict below) | `Wire.h` `LiquidCrystal_I2C.h` |
| SmartHouse_v1/Door_Servo_UltrasonicAutoOpen | Uno | #3 Servo | `Servo.h` |
| SmartHouse_v1/Aug16a_ESP32_WiFi_LED_WebAPI | ESP32 | ESP32 board package + create `arduino_secrets.h` | `WiFi.h` `WebServer.h` `arduino_secrets.h` |

### Build check after installing (2026-09-26)
With the libraries above installed, **53 of 55 sketches build**. The two that do not:
- `SmartHouse_v1/Jun14a_LCD_I2C_PrintName` needs the one-line `lcd.init()` fix.
- `WIP_Bird_Empty` has no code yet.

---

## ⚠️ Common problems
| Error message | Fix |
|---|---|
| `Servo.h: No such file or directory` (or any `xxx.h: No such file`) | That library isn't installed. Find the header in the table above and install it |
| `no matching function for call to 'LiquidCrystal_I2C::begin()'` | Use `lcd.init();`. See the conflict below |
| `'IrReceiver' was not declared` / `IRremote.hpp: No such file` | An old IRremote (2.x/3.x) is installed. Update it to **4.x** |
| `WiFi.h: No such file` or `Preferences.h: No such file` | The board is set to Uno. Choose **ESP32 Dev Module** |
| `arduino_secrets.h: No such file` | Copy `arduino_secrets.example.h` to `arduino_secrets.h` in the same folder |
| `Multiple libraries were found for "LiquidCrystal_I2C.h"` | Two LCD libraries are installed. See below |
| LCD lights up but shows no text | Address is 0x3F, not 0x27 (run `Tool_I2C_Scanner`), or turn the contrast screw |

### Duplicate LCD library conflict
Two folders in `libraries/` both provide `LiquidCrystal_I2C.h`:

| Folder | Init call | Keep? |
|---|---|---|
| `LiquidCrystal_I2C` (Frank de Brabander 1.1.2, from Library Manager) | `lcd.init();` | ✅ **keep**: every sketch except Jun14a uses it |
| `Arduino-LiquidCrystal-I2C-library-master` (manually downloaded ZIP) | `lcd.begin();` | ❌ delete after fixing Jun14a |

The compiler currently chooses the correct one, but fixing `Jun14a` and deleting the ZIP copy removes the ambiguity.

---

## Other libraries in `libraries/` (installed, not used by any sketch yet)
Kept for future projects: MD_Parola 3.7.7 + MD_MAX72XX 3.5.1 (scrolling text on LED matrices), U8g2 2.36.19, Adafruit SSD1306 2.5.17 / SSD1305 2.2.3 / SSD1331 1.3.0 (OLEDs), Adafruit LiquidCrystal 2.0.4, Adafruit MCP23017 2.3.2, Adafruit seesaw 1.7.9, LiquidCrystal 1.0.7, Keypad 3.1.1, SD 1.3.0, Arduino_AVRSTL 1.2.5, EasyESPConnect 1.1.1, EasyPreferences 0.1.4, MatrixForge 1.0.0.
