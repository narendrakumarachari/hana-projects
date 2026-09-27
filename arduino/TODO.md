# To-do list (all projects)

Collected from the code review of every sketch on **2026-09-26**. Each project's `README.md` has the same items with more detail.
Tick them off here as you go.

## 🔴 Do before / right after uploading
- [x] **Install the Servo library** (Tools → Manage Libraries → "Servo" by Arduino). Without it these 4 don't build: `SmartHouse_v1`, `Door_Servo_ButtonOpen`, `Door_RFID_AccessControl`, `SmartHouse_v1/Door_Servo_UltrasonicAutoOpen`.
- [ ] Check that `arduino_secrets.h` is **not** being uploaded (run `git status`; see README → Uploading).
- [x] Decide on the names in the code (Krish, Hana, and the full name in `Jun14a`): public or private repo?
- [x] Delete the 3 exact duplicates (`tr66b`, `hexmap123`, `sketch_jun16b`). Done 2026-09-26.
- [ ] `WIP_Bird_Empty`: give it a goal or delete it.

## 🟠 Real bugs found in review
- [ ] **Sensor_ParkingSensor_Ultrasonic**: with nothing in range, it buzzes non-stop (`pulseIn` returns 0 → "0 cm"). Add a timeout and treat 0 as far.
- [ ] **Security_ObjectRemovedAlarm / NightTheftAlarm / TheftDetector_PoliceSiren**: no echo reads as "object present", so the alarm fails silently. Add a `pulseIn` timeout.
- [ ] **Sensor_AutoNightLight_LDR / Security_NightTheftAlarm**: LDR readings below 650 (the darkest range) are ignored.
- [ ] **Security_TheftDetector_PoliceSiren**: the siren only chirps once every 3 s. Latch the alarm on.
- [ ] **LED_Scanner_DualBuzzer_Show**: buzzer 2 never sounds (Uno plays one `tone()` at a time).
- [ ] **Project_HanaMiniTV_IR_LCD**: Showcase channel corrupts the Dino/Hero graphics. Reset `dinoInited`/`heroInited` on each sub-channel switch.
- [ ] **Project_HanaMiniTV_IR_LCD**: 6 LCD texts are longer than 16 characters and get cut off.
- [x] **SmartHouse_v1/Jun14a_LCD_I2C_PrintName**: changed `lcd.begin()` → `lcd.init()` (2026-09-26).
- [ ] **Sound_ClapSensor_MarioMelody**: "Clap"/"No Clap" labels look swapped, and it floods the Serial Monitor.

## 🟡 Clean-ups
- [x] Deleted `libraries/Arduino-LiquidCrystal-I2C-library-master` (duplicate LCD library).
- [ ] **IR_RemoteButtons_LCD**: remove the stray `0` / `;` line, and add button 8 (`0xAD52FF00`), NEXT (`0xBC39FF00`) and EQ.
- [ ] **Door_Servo_ButtonOpen**: use `attach(servoPin)` instead of `attach(10)`. The `images/` show the old stock example, not this circuit.
- [ ] **Display_LEDMatrix_LetterK**: rename the array `one` → `letterK`.
- [ ] **SmartHouse_v1**: the active buzzer on D5 is never used, and it should guard against a `NaN` temperature.
- [ ] **Game_SkyGuardian_LCD**: flickers (clears the LCD every frame). Auto-format the dense code.
- [ ] **Project_HanaMiniTV_IR_LCD**: reduce flicker in channels 1 and 4–8.
- [ ] **Sound_LoudnessAlarm_Analog**: samples only once a second, so it misses claps.
- [ ] **Music_HappyBirthday_Serial**: replace the hard-coded `25` with a computed length.
- [ ] **SkyGuardTFT**: optionally rename to `Game_SkyGuard_ESP32_TFT` (close the IDE first, rename the folder **and** the `.ino`).
- [ ] **Input_Button_SerialEvent**: write down what PC program read its output.

## 🟢 Nice-to-have ideas
- [ ] **ESP32_WiFi_LED_WebAPI**: a home page with buttons, a Wi-Fi timeout, mDNS (`esp32.local`).
- [ ] **SmartHouse v2**: control it with the IR remote or over Wi-Fi instead of the USB cable.
- [ ] **Game_FlappyBird_LCD**: save the high score in EEPROM.
- [ ] **Display_LEDMatrix_LetterK**: scroll text with MD_Parola (already installed).
- [ ] **Music_HappyBirthday_LEDShow**: start button instead of looping forever.
- [ ] **LCD_SerialMessageBoard**: word wrap and scrolling for long messages.
- [ ] **SmartHouse_v1**: move the 22 learning sketches to a top-level `Learning_Steps/` folder.
- [ ] Add photos or wiring diagrams to the main projects.

## Per-project checklist
| Project | Open to-dos |
|---|---|
| Basics_HelloWorld_Serial | — |
| LED_RGB_ColorCycle | optional mixed colours |
| LED_Scanner_Buzzer | optional speed constant |
| LED_Scanner_DualBuzzer_Show | 2nd buzzer fix, hard-coded pins |
| Music_HappyBirthday_Serial | computed length |
| Music_HappyBirthday_LEDShow | optional start button |
| Sound_RandomBirdChirps | optional dawn-chorus LDR |
| Sound_BirdPiano_5Buttons | optional button pictures, usage log |
| Sound_ClapDetect_LED_Buzzer | — |
| Sound_ClapSensor_MarioMelody | polarity check, serial flood |
| Sound_LoudnessAlarm_Analog | faster sampling, threshold constant |
| Sensor_AutoNightLight_LDR | < 650 gap, optional smooth fade |
| Sensor_ParkingSensor_Ultrasonic | **pulseIn timeout bug** |
| Security_ObjectRemovedAlarm | pulseIn timeout |
| Security_NightTheftAlarm | keep or delete (superseded) |
| Security_TheftDetector_PoliceSiren | latch alarm, < 650 light, timeout |
| Door_Servo_ButtonOpen | `attach(servoPin)`, diagram |
| Door_RFID_AccessControl | optional multi-card |
| IR_RemoteCodeReader | — |
| IR_RemoteButtons_LCD | stray line, missing buttons, repeat codes |
| LCD_SerialMessageBoard | optional wrap/scroll |
| Display_LEDMatrix_LetterK | rename array, optional scroll |
| Input_Button_SerialEvent | document the PC side |
| Game_SkyGuardian_LCD | flicker, auto-format |
| Game_FlappyBird_LCD | optional EEPROM high score |
| SkyGuardTFT | optional rename, photo |
| Project_HanaMiniTV_IR_LCD | Showcase bug, long strings, flicker |
| ESP32_WiFi_LED_WebAPI | home page, timeout, mDNS |
| Tool_I2C_Scanner | — |
| Tool_ST7789_WiringFinder | — |
| Tool_ST7789_HealthCheck | — |
| WIP_Bird_Empty | define or delete |
| SmartHouse_v1 (main) | D5 buzzer, NaN temp, v2 ideas |
| SmartHouse_v1 learning sketches | optional move |
