#include <WiFi.h>
#include <WebServer.h>
#include "arduino_secrets.h"   // Wi-Fi name + password (not uploaded to GitHub)

const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;

WebServer server(80);

const int LED = 2;

// /on
void handleOn() {
  digitalWrite(LED, HIGH);
  server.send(200, "text/plain", "LED ON");
}

// /off
void handleOff() {
  digitalWrite(LED, LOW);
  server.send(200, "text/plain", "LED OFF");
}

// /
void handlebird() {
  digitalWrite(LED, HIGH);
  delay(500);

  digitalWrite(LED, LOW);
  delay(500);

  server.send(200, "text/plain", "bird - LED blinked");
}

void setup() {

  Serial.begin(9600);

  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);

  // Connect Wi-Fi
  WiFi.begin(ssid, password);

  Serial.print("Connecting");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");

  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Endpoints
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.on("/bird", handlebird);

  server.begin();

  Serial.println("HTTP server started");
  Serial.println("LED STARTED");
}

void loop() {
  server.handleClient();
}