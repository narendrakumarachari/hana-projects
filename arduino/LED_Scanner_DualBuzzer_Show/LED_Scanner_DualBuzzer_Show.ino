// ==========================================
// Smooth LED Scanner + Dual Passive Buzzers
// LEDs : 4 - 13
// Buzzer 1 : Pin 2
// Buzzer 2 : Pin 3
// ==========================================

const byte ledPins[] = {4,5,6,7,8,9,10,11,12,13};
const byte NUM_LEDS = 10;

const byte buzzer1 = 2;
const byte buzzer2 = 3;

// Musical notes
int notes[] = {
  262,294,330,349,392,
  440,494,523,587,659
};

void setup()
{
  for(byte i=0;i<NUM_LEDS;i++)
  {
    pinMode(ledPins[i],OUTPUT);
    digitalWrite(ledPins[i],LOW);
  }

  pinMode(buzzer1,OUTPUT);
  pinMode(buzzer2,OUTPUT);
}

void loop()
{
  // Left to Right
  for(int i=0;i<NUM_LEDS;i++)
  {
    showScanner(i);

    tone(buzzer1, notes[i], 70);
    tone(buzzer2, notes[NUM_LEDS-1-i], 70);

    delay(90);
  }

  // Right to Left
  for(int i=NUM_LEDS-2;i>=1;i--)
  {
    showScanner(i);

    tone(buzzer1, notes[i], 70);
    tone(buzzer2, notes[NUM_LEDS-1-i], 70);

    delay(90);
  }

  // Smooth Wave Effect
  for(int r=0;r<4;r++)
  {
    for(int i=0;i<NUM_LEDS;i++)
    {
      digitalWrite(ledPins[i],HIGH);

      tone(buzzer1,400+i*40,40);
      tone(buzzer2,800-i*30,40);

      delay(45);
    }

    for(int i=NUM_LEDS-1;i>=0;i--)
    {
      digitalWrite(ledPins[i],LOW);

      tone(buzzer1,800-i*30,40);
      tone(buzzer2,400+i*40,40);

      delay(45);
    }
  }

  // Center Expand
  for(int k=0;k<3;k++)
  {
    clearAll();

    digitalWrite(7,HIGH);
    digitalWrite(8,HIGH);
    tone(buzzer1,700,60);
    tone(buzzer2,900,60);
    delay(100);

    digitalWrite(6,HIGH);
    digitalWrite(9,HIGH);
    delay(100);

    digitalWrite(5,HIGH);
    digitalWrite(10,HIGH);
    delay(100);

    digitalWrite(4,HIGH);
    digitalWrite(11,HIGH);
    delay(100);

    digitalWrite(12,HIGH);
    digitalWrite(13,HIGH);
    delay(100);

    clearAll();
    delay(120);
  }

  // Blink Finale
  for(int j=0;j<8;j++)
  {
    for(int i=0;i<NUM_LEDS;i++)
      digitalWrite(ledPins[i],HIGH);

    tone(buzzer1,1000,80);
    tone(buzzer2,1300,80);
    delay(100);

    clearAll();
    delay(100);
  }
}

void showScanner(int pos)
{
  clearAll();

  digitalWrite(ledPins[pos],HIGH);

  if(pos>0)
    digitalWrite(ledPins[pos-1],HIGH);

  if(pos<NUM_LEDS-1)
    digitalWrite(ledPins[pos+1],HIGH);
}

void clearAll()
{
  for(byte i=0;i<NUM_LEDS;i++)
    digitalWrite(ledPins[i],LOW);
}