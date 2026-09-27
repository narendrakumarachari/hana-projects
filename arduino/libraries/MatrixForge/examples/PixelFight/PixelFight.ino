#include "PixelFightGame.h"
#include <Wire.h>

PixelFightGame game;

void setup()
{
    Serial.begin(115200);

    Wire.begin(I2C_SDA, I2C_SCL);

    game.begin();

    Serial.println("Pixel Fight Started");
}

void loop()
{
    game.update();
    game.render();

    delay(10);
}