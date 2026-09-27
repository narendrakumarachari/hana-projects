String command = "";

void setup() {
  pinMode(13, OUTPUT);
  Serial.begin(9600);

  Serial.println("Type ON or OFF");
}

void loop() {
  if (Serial.available()) {
    command = Serial.readStringUntil('\n');
    command.trim();

    command.toUpperCase();

    if (command == "ON") {
      digitalWrite(13, HIGH);
      Serial.println("LED ON");
    }
    else if (command == "OFF") {
      digitalWrite(13, LOW);
      Serial.println("LED OFF");
    }
    else {
      Serial.println("Invalid Command");
    }
  }
}