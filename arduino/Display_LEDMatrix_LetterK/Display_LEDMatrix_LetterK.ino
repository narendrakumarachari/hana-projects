#include <LedControl.h>

LedControl lc = LedControl(12, 11, 10, 1);

byte one[8] = {
  B01000100,
  B01001000,
  B01010000,
  B01100000,
  B01100000,
  B01010000,
  B01001000,
  B01000100
};

void setup() {
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);

  for (int i = 0; i < 8; i++) {
    lc.setRow(0, i, one[i]);
  }
}

void loop() {
}