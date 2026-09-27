#include <IRremote.hpp>

#define IR_RECEIVE_PIN 2

void setup() {
  Serial.begin(9600);

  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);

  Serial.println("IR Receiver Ready...");
}

void loop() {

  if (IrReceiver.decode()) {

    // Serial.print("HEX Code : 0x");
    Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);

    // Serial.print("Protocol : ");
    // Serial.println(getProtocolString(IrReceiver.decodedIRData.protocol));

    // Serial.print("Command  : 0x");
    // Serial.println(IrReceiver.decodedIRData.command, HEX);

    // Serial.print("Address  : 0x");
    // Serial.println(IrReceiver.decodedIRData.address, HEX);

    // Serial.println("------------------------");

    IrReceiver.resume();
  }
} 