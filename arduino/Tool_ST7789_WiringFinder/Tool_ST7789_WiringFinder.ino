// Screen finder for the 1.54" ST7789 on the ESP32.
// Tries the correct wiring and the most common wire mix-ups, one after another.
// Each try fills the screen red, green, blue with "TEST n" in big letters.
// If the screen lights up on a test, that number tells us what's wrong.
#include <Adafruit_GFX.h>
#include <Adafruit_ST7789.h>
#include <SPI.h>

// Correct wiring from the game
#define P_SCL 18
#define P_SDA 23
#define P_RST 4
#define P_DC  2
#define P_CS  5

struct Try { const char *what; int8_t cs, dc, sda, scl, rst; uint8_t mode; };

const Try tries[] = {
  {"correct wiring",          P_CS,  P_DC,  P_SDA, P_SCL, P_RST, SPI_MODE0},
  {"correct wiring, mode 3",  P_CS,  P_DC,  P_SDA, P_SCL, P_RST, SPI_MODE3},
  {"SCL and SDA swapped",     P_CS,  P_DC,  P_SCL, P_SDA, P_RST, SPI_MODE0},
  {"DC and CS swapped",       P_DC,  P_CS,  P_SDA, P_SCL, P_RST, SPI_MODE0},
  {"DC and RST swapped",      P_CS,  P_RST, P_SDA, P_SCL, P_DC,  SPI_MODE0},
  {"CS and RST swapped",      P_RST, P_DC,  P_SDA, P_SCL, P_CS,  SPI_MODE0},
};
const int NUM_TRIES = sizeof(tries) / sizeof(tries[0]);

void runTry(int n) {
  const Try &t = tries[n];
  Serial.printf("TEST %d: %s\n", n + 1, t.what);
  // Software SPI so any pin can play any role
  Adafruit_ST7789 *tft = new Adafruit_ST7789(t.cs, t.dc, t.sda, t.scl, t.rst);
  tft->init(240, 240, t.mode);
  char label[12];
  snprintf(label, sizeof(label), "TEST %d", n + 1);
  uint16_t colors[] = {ST77XX_RED, ST77XX_GREEN, ST77XX_BLUE};
  for (uint16_t c : colors) {
    tft->fillScreen(c);
    tft->setTextSize(5);
    tft->setTextColor(ST77XX_WHITE);
    tft->setCursor(30, 100);
    tft->print(label);
    delay(400);
  }
  delete tft;
  // release the pins before the next try
  int8_t pins[] = {t.cs, t.dc, t.sda, t.scl, t.rst};
  for (int8_t p : pins) pinMode(p, INPUT);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  Serial.println("\nScreen finder starting");
}

void loop() {
  for (int n = 0; n < NUM_TRIES; n++) runTry(n);
}
