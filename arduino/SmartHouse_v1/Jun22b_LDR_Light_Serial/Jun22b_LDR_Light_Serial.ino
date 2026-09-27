int ldrPin = A0;

void setup() {
  Serial.begin(9600);
  Serial.println("LDR Raw Reading Started");
}

void loop() {
  int ldrValue = analogRead(ldrPin);

  Serial.print("LDR Value: ");
  Serial.println(ldrValue);

  delay(1000);
}