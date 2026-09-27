const byte ledPins[10] = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11};



const byte buzzerPin = 12;

const byte buttonPin = 13;



byte mode = 0;

bool lastButton = HIGH;



//--------------------------------------------------------



void allOff() {

  for (byte i = 0; i < 10; i++) {

    digitalWrite(ledPins[i], LOW);

  }

}



//--------------------------------------------------------



void beep() {

  tone(buzzerPin, 2000, 80);

}



//--------------------------------------------------------



void setup() {



  Serial.begin(9600);



  for (byte i = 0; i < 10; i++) {

    pinMode(ledPins[i], OUTPUT);

  }



  pinMode(buttonPin, INPUT_PULLUP);

  pinMode(buzzerPin, OUTPUT);



  allOff();



  Serial.println("Pattern 1");

}



//--------------------------------------------------------



void loop() {



  bool button = digitalRead(buttonPin);



  // Button Pressed

  if (button == LOW && lastButton == HIGH) {



    mode++;

    if (mode > 3) mode = 0;



    beep();



    Serial.print("Pattern Changed -> ");

    Serial.println(mode + 1);



    delay(180);      // debounce

  }



  lastButton = button;



  switch (mode) {



    case 0:

      pattern1();

      break;



    case 1:

      pattern2();

      break;



    case 2:

      pattern3();

      break;



    case 3:

      pattern4();

      break;

  }

}



//========================================================

// PATTERN 1 : Fast Left to Right

//========================================================



void pattern1() {



  static byte i = 0;

  static unsigned long t = 0;



  if (millis() - t >= 50) {



    allOff();

    digitalWrite(ledPins[i], HIGH);



    i++;

    if (i >= 10) i = 0;



    t = millis();

  }

}



//========================================================

// PATTERN 2 : Fast Right to Left

//========================================================



void pattern2() {



  static int i = 9;

  static unsigned long t = 0;



  if (millis() - t >= 50) {



    allOff();

    digitalWrite(ledPins[i], HIGH);



    i--;

    if (i < 0) i = 9;



    t = millis();

  }

}



//========================================================

// PATTERN 3 : Bounce

//========================================================



void pattern3() {



  static int i = 0;

  static int dir = 1;

  static unsigned long t = 0;



  if (millis() - t >= 40) {



    allOff();

    digitalWrite(ledPins[i], HIGH);



    i += dir;



    if (i >= 9) dir = -1;

    if (i <= 0) dir = 1;



    t = millis();

  }

}



//========================================================

// PATTERN 4 : Even/Odd Flash

//========================================================



void pattern4() {



  static bool state = false;

  static unsigned long t = 0;



  if (millis() - t >= 70) {



    allOff();



    if (state) {

      for (byte i = 0; i < 10; i += 2)

        digitalWrite(ledPins[i], HIGH);

    } else {

      for (byte i = 1; i < 10; i += 2)

        digitalWrite(ledPins[i], HIGH);

    }



    state = !state;

    t = millis();

  }

}