// ======================================================================
//  LED Brightness Web Slider  (the board half of the "LED from anywhere"
//  demo). Shared by the teacher in class on 2026-08-07.
//
//  WHAT IT DOES
//   Waits for a number from the computer (0 to 255) and sets the LED's
//   brightness to that number. 0 = off, 255 = full brightness.
//
//  WHO SENDS THE NUMBER?
//   The Python web page  python/03_Arduino_ESP32_Companions/
//   web_led_brightness_slider.py  sends it over the USB cable every
//   time someone moves the slider. With ngrok, that someone can be
//   anywhere in the world!
//
//  WIRING
//   LED long leg (+) -> 220 ohm resistor -> pin 11
//   LED short leg (-) -> GND
//
//  TIPS
//   - Pin 11 has a "~" next to it: that means it can dim (PWM).
//   - Close the Serial Monitor before starting the Python program:
//     only one program can use the USB port at a time.
// ======================================================================

const int LED_PIN = 11;          // a "~" pin, so analogWrite can dim it

void setup() {
  pinMode(LED_PIN, OUTPUT);
  Serial.begin(9600);            // must match BAUD in the Python program
  analogWrite(LED_PIN, 0);       // start with the LED off
}

void loop() {
  if (Serial.available()) {                    // did the computer send something?
    int brightness = Serial.parseInt();        // read the number, e.g. "128"
    brightness = constrain(brightness, 0, 255); // keep it between 0 and 255
    analogWrite(LED_PIN, brightness);          // set the brightness
    Serial.println(brightness);                // say back what we did
  }
}
