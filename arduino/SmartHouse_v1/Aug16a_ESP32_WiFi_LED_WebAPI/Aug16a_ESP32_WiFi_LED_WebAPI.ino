#include <WiFi.h>
#include <WebServer.h>
#include "arduino_secrets.h"   // Wi-Fi name + password (not uploaded to GitHub)

// Wi-Fi credentials come from arduino_secrets.h
const char* ssid = SECRET_SSID;
const char* password = SECRET_PASS;

// Create web server on port 80
WebServer server(80);

// ESP32 built-in LED
const int LED = 23;

// /on endpoint
void handleOn() {
  digitalWrite(LED, HIGH);
  server.send(200, "text/plain", "LED ON");
}

// /off endpoint
void handleOff() {
  digitalWrite(LED, LOW);
  server.send(200, "text/plain", "LED OFF");
}

void handlePoP() {
  digitalWrite(LED, HIGH);
  delay(1000);
  digitalWrite(LED, LOW);
  delay(1000);
  server.send(200, "text/plain", "led blinking");
}


void setup() {
  Serial.begin(9600);

  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);

  // Connect to Wi-Fi
  WiFi.begin(ssid, password);

  Serial.print("Connecting to Wi-Fi");

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Wi-Fi connected!");
  Serial.print("ESP32 IP: ");
  Serial.println(WiFi.localIP());

  // Define endpoints
  server.on("/on", handleOn);
  server.on("/off", handleOff);
  server.on("/PoP", handlePoP);
  // Start server
  server.begin();

  Serial.println("HTTP server started");
}

void loop() {
  server.handleClient();
}