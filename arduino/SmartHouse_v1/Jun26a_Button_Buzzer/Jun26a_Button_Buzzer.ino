// =============================
// Push Button + Buzzer Test
// Buzzer  : Pin 12
// Button  : Pin 13
// =============================

const int buzzerPin = 12;
const int buttonPin = 13;

bool lastButtonState = HIGH;

void setup() {
  pinMode(buzzerPin, OUTPUT);

  // Using internal pull-up resistor
  pinMode(buttonPin, INPUT_PULLUP);

  Serial.begin(9600);

  digitalWrite(buzzerPin, LOW);

  Serial.println("=== Push Button Test Started ===");
}

void loop() {

  bool buttonState = digitalRead(buttonPin);

  // Button Pressed
  if (buttonState == LOW && lastButtonState == HIGH) {
    Serial.println("Push Button Pressed");

    tone(buzzerPin, 1000);   // 1000 Hz beep
  }

  // Button Released
  if (buttonState == HIGH && lastButtonState == LOW) {
    Serial.println("Push Button Released");

    noTone(buzzerPin);
  }

  lastButtonState = buttonState;

  delay(20); // Debounce
}