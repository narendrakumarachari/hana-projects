// Is the 1.54" ST7789 screen dead? Open Serial Monitor at 115200 to see the answer.
// Same wiring as Sky Guard: SCL 18, SDA 23, RST 4, DC 2, CS 5, VCC + BL to 3.3V.
//
// Step 1: checks each wire isn't shorted (a burnt chip often shorts its pins).
// Step 2: asks the screen chip for its ID number. A live ST7789 answers,
//         a dead one (or a loose wire) stays silent.
// Step 3: if it answered, fills the screen red / green / blue / white.
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

#define TFT_SCL 18
#define TFT_SDA 23
#define TFT_RST 4
#define TFT_DC  2
#define TFT_CS  5

bool pinsOk = true;

// Drive a pin high then low and read it back. If it can't reach a level,
// something on that wire (or inside the screen) is pulling it.
void checkPin(const char *name, int pin) {
  pinMode(pin, OUTPUT);
  digitalWrite(pin, HIGH); delay(5);
  bool high = digitalRead(pin);
  digitalWrite(pin, LOW);  delay(5);
  bool low = !digitalRead(pin);
  Serial.printf("  %-4s GPIO %-2d : %s\n", name, pin,
                high && low ? "OK" : !high ? "STUCK LOW (shorted to GND?)" : "STUCK HIGH (shorted to 3.3V?)");
  if (!(high && low)) pinsOk = false;
}

void sendByte(uint8_t b) {
  for (int i = 7; i >= 0; i--) {
    digitalWrite(TFT_SDA, (b >> i) & 1);
    digitalWrite(TFT_SCL, HIGH); delayMicroseconds(2);
    digitalWrite(TFT_SCL, LOW);  delayMicroseconds(2);
  }
}

// Send "read display ID" (0x04) by hand, then let go of SDA and listen.
// pullMode decides which way the SDA line floats if nobody is talking.
uint32_t readId(uint8_t pullMode) {
  pinMode(TFT_SDA, OUTPUT);
  digitalWrite(TFT_CS, LOW);
  digitalWrite(TFT_DC, LOW);           // command
  sendByte(0x04);
  pinMode(TFT_SDA, pullMode);          // the screen talks back on the same wire
  digitalWrite(TFT_DC, HIGH);
  uint32_t v = 0;
  for (int i = 0; i < 32; i++) {       // 1 dummy bit + 24 ID bits + spare
    digitalWrite(TFT_SCL, HIGH); delayMicroseconds(2);
    v = (v << 1) | digitalRead(TFT_SDA);
    digitalWrite(TFT_SCL, LOW);  delayMicroseconds(2);
  }
  digitalWrite(TFT_CS, HIGH);
  pinMode(TFT_SDA, OUTPUT);
  return v;
}

void colorTest(uint8_t mode, const char *label) {
  Serial.printf("  Filling colors (%s) - look at the screen\n", label);
  Adafruit_ST7789 tft(TFT_CS, TFT_DC, TFT_RST);
  tft.init(240, 240, mode);
  uint16_t colors[] = {ST77XX_RED, ST77XX_GREEN, ST77XX_BLUE, ST77XX_WHITE};
  for (uint16_t c : colors) { tft.fillScreen(c); delay(700); }
  tft.setTextSize(4);
  tft.setTextColor(ST77XX_BLACK);
  tft.setCursor(20, 100);
  tft.print("ALIVE!");
  delay(1500);
}

void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n===== TFT health check =====");

  Serial.println("Step 1: wire check");
  checkPin("SCL", TFT_SCL);
  checkPin("SDA", TFT_SDA);
  checkPin("RST", TFT_RST);
  checkPin("DC",  TFT_DC);
  checkPin("CS",  TFT_CS);

  // Reset the screen chip
  digitalWrite(TFT_CS, HIGH);
  digitalWrite(TFT_SCL, LOW);
  digitalWrite(TFT_RST, LOW);  delay(20);
  digitalWrite(TFT_RST, HIGH); delay(150);

  Serial.println("Step 2: asking the screen chip for its ID");
  uint32_t up   = readId(INPUT_PULLUP);
  uint32_t down = readId(INPUT_PULLDOWN);
  Serial.printf("  answer with pull-up   : %08lX\n", (unsigned long)up);
  Serial.printf("  answer with pull-down : %08lX\n", (unsigned long)down);

  // If nobody talks, the line just follows the pull: FFFFFFFF vs 00000000.
  // If the chip talks, both reads show the same real number (ST7789 is 85 85 52).
  bool answered = (up == down) && up != 0 && up != 0xFFFFFFFF;

  Serial.println("\n===== RESULT =====");
  if (answered) {
    Serial.println("The screen chip ANSWERED. It is NOT burnt up.");
    Serial.println("Step 3: color test");
    SPI.begin(TFT_SCL, -1, TFT_SDA, TFT_CS);
    colorTest(SPI_MODE0, "mode 0");
    colorTest(SPI_MODE3, "mode 3");
    Serial.println("If the colors showed, the screen works. If they didn't, the");
    Serial.println("backlight (BL pin / LED) is the likely problem, not the chip.");
  } else if (!pinsOk) {
    Serial.println("A wire is SHORTED (see Step 1). Unplug the screen and run again:");
    Serial.println(" - still shorted without the screen -> the ESP32 pin or breadboard is the problem");
    Serial.println(" - fine without the screen          -> the screen is shorted inside = burnt");
  } else {
    Serial.println("The screen chip did NOT answer.");
    Serial.println("Before calling it dead: re-seat every wire, confirm VCC really has 3.3V,");
    Serial.println("and try once more. Some modules can't answer on SDA - if the backlight");
    Serial.println("glows and nothing is hot, it may still be alive (inconclusive).");
  }
}

void loop() {}
