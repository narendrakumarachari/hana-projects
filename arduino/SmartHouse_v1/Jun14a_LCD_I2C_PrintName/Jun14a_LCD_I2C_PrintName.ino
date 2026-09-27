#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Create LCD object with I2C address 0x27 and 16 columns x 2 rows
LiquidCrystal_I2C lcd(0x27, 16, 2);

void setup()
{
    // Initialize the LCD
    lcd.begin();

    // Turn on the backlight
    // lcd.noBacklight();
    lcd.backlight();
    // Set cursor
    lcd.setCursor(0, 0);

    // Print text
    lcd.print("Chaarvi Guduru");
}

void loop()
{
    // Nothing to do here
}