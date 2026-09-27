#include <SPI.h>
#include <MFRC522.h>
#include <Servo.h>

#define SS_PIN 10
#define RST_PIN 9
#define SERVO_PIN 6
#define BUZZER_PIN 3

MFRC522 rfid(SS_PIN, RST_PIN);
Servo doorServo;

// Authorized RFID UID
byte authorizedUID[] = {0xF1, 0x8A, 0xBC, 0x5C};

void setup() {
  Serial.begin(9600);

  SPI.begin();
  rfid.PCD_Init();

  doorServo.attach(SERVO_PIN);
  doorServo.write(0);  // Door locked

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.println("RFID Door Access System");
  Serial.println("Scan your RFID card...");
}

void loop() {

  // Check for new card
  if (!rfid.PICC_IsNewCardPresent()) {
    return;
  }

  // Read card UID
  if (!rfid.PICC_ReadCardSerial()) {
    return;
  }

  Serial.print("\nCard UID: ");

  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) {
      Serial.print("0");
    }

    Serial.print(rfid.uid.uidByte[i], HEX);

    if (i < rfid.uid.size - 1) {
      Serial.print(":");
    }
  }

  Serial.println();

  // Check whether UID is authorized
  if (checkUID()) {

    Serial.println("ACCESS GRANTED");
    Serial.println("Door Opening...");

    successBuzzer();

    // Open door
    doorServo.write(90);

    delay(3000);

    // Close door
    doorServo.write(0);

    Serial.println("Door Closed");
  }

  else {

    Serial.println("ACCESS DENIED");
    Serial.println("Wrong RFID Card!");

    wrongBuzzer();

    // Make sure door remains locked
    doorServo.write(0);
  }

  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();

  delay(500);
}


// ---------------------------
// CHECK AUTHORIZED UID
// ---------------------------

bool checkUID() {

  // UID must have same number of bytes
  if (rfid.uid.size != sizeof(authorizedUID)) {
    return false;
  }

  for (byte i = 0; i < rfid.uid.size; i++) {

    if (rfid.uid.uidByte[i] != authorizedUID[i]) {
      return false;
    }
  }

  return true;
}


// ---------------------------
// SUCCESS BUZZER
// Beep-Beep
// ---------------------------

void successBuzzer() {

  tone(BUZZER_PIN, 1500);
  delay(100);
  noTone(BUZZER_PIN);

  delay(100);

  tone(BUZZER_PIN, 2000);
  delay(150);
  noTone(BUZZER_PIN);
}


// ---------------------------
// WRONG CARD BUZZER
// Long warning sound
// ---------------------------

void wrongBuzzer() {

  tone(BUZZER_PIN, 500);
  delay(250);
  noTone(BUZZER_PIN);

  delay(100);

  tone(BUZZER_PIN, 500);
  delay(250);
  noTone(BUZZER_PIN);

  delay(100);

  tone(BUZZER_PIN, 300);
  delay(500);
  noTone(BUZZER_PIN);
}