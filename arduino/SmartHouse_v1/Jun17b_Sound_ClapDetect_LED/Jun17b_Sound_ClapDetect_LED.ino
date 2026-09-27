int soundPin = 12;

int ledPin = 13;



void setup() {

  pinMode(soundPin, INPUT);

  pinMode(ledPin, OUTPUT);



  Serial.begin(9600);

  Serial.println("Sound Detection Started");

}



void loop() {

  int soundState = digitalRead(soundPin);



  if (soundState == HIGH) {   // Change to LOW if needed

    Serial.println("clap detected");

    digitalWrite(ledPin, HIGH);

  }

  else {

    digitalWrite(ledPin, LOW);

  }



  delay(100);

}