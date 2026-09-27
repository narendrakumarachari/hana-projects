#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <IRremote.hpp>

#define IR_RECEIVE_PIN 2

LiquidCrystal_I2C lcd(0x27, 16, 2);

void showButton(String text)
{
  Serial.println(text);

  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Button:");
  lcd.setCursor(0,1);
  lcd.print(text);
}

void setup()
{
  Serial.begin(9600);

  lcd.init();
  lcd.backlight();

  lcd.setCursor(0,0);
  lcd.print("IR Remote");
  lcd.setCursor(0,1);
  lcd.print("Ready");

  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);
}

void loop()
{
  if (IrReceiver.decode())
  {
    uint32_t code = IrReceiver.decodedIRData.decodedRawData;

    switch(code)
    {
      case 0xBA45FF00:
        showButton("POWER");
        break;

      case 0xB946FF00:
        showButton("VOL+");
        break;

      case 0xB847FF00:
        showButton("FUNC/STOP");
        break;

      case 0xBB44FF00:
        showButton("PREVIOUS");
        break;

      case 0xBF40FF00:
        showButton("PLAY/PAUSE");
        break;
      
      case 0xF609FF00:
        showButton("Up");
        break;

      case 0xF807FF00:
        showButton("DOWN");
        break;

      case 0xEA15FF00:
        showButton("VOL-");
        break;
0
      ;case 0xF20DFF00:
        showButton("Repeat");
        break;

      case 0xE916FF00:
        showButton("0");
        break;

      case 0xF30CFF00:
        showButton("1");
        break;

      case 0xE718FF00:
        showButton("2");
        break;

      case 0xA15EFF00:
        showButton("3");
        break;

      case 0xF708FF00:
        showButton("4");
        break;

      case 0xE31CFF00:
        showButton("5");
        break;

      case 0xA55AFF00:
        showButton("6");
        break;

      case 0xBD42FF00:
        showButton("7");
        break;
  
        case 0xB54AFF00:
        showButton("9");
        break;

      default:
        Serial.print("Unknown: 0x");
        Serial.println(code, HEX);

        lcd.clear();
        lcd.print("Unknown");
        lcd.setCursor(0,1);
        lcd.print(code, HEX);
        break;
    }

    IrReceiver.resume();
  }
}