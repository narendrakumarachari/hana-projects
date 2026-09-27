const int buttonPin = 11;

bool lastState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

void setup() {
  pinMode(buttonPin, INPUT_PULLUP);
  Serial.begin(9600);

  Serial.println("Button Ready");
}

void loop() {
  bool currentState = digitalRead(buttonPin);

  if (currentState != lastState) {
    lastDebounceTime = millis();
  }

  if ((millis() - lastDebounceTime) > debounceDelay) {
    static bool buttonState = HIGH;

    if (currentState != buttonState) {
      buttonState = currentState;

      if (buttonState == LOW) {
        Serial.println("BUTTON_PRESSED");
        Serial.println("=");
      }
    }
  }

  lastState = currentState;
}