#include <Wire.h>
#include <LiquidCrystal_I2C.h>

LiquidCrystal_I2C lcd(0x27, 16, 2); // change to 0x3F if 0x27 doesn't work

String inputBuffer = "";

void setup() {
  Serial.begin(9600);
  lcd.init();
  lcd.backlight();

  lcd.setCursor(0, 0);
  lcd.print("Send msg via");
  lcd.setCursor(0, 1);
  lcd.print("Serial Monitor");
}

void loop() {
  while (Serial.available() > 0) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        showMessage(inputBuffer);
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
    }
  }
}

void showMessage(String msg) {
  lcd.clear();

  if (msg.length() <= 16) {
    // fits on one line
    lcd.setCursor(0, 0);
    lcd.print(msg);
  } else {
    // split across two lines (16 chars each)
    lcd.setCursor(0, 0);
    lcd.print(msg.substring(0, 16));
    lcd.setCursor(0, 1);
    lcd.print(msg.substring(16, 32)); // truncates beyond 32 chars total
  }
}