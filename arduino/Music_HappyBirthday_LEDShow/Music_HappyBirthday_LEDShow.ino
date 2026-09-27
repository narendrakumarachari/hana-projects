// =========================================
// Happy Birthday with LED Show
// Passive Buzzer -> Pin 3
// LEDs -> Pins 4 to 13
// =========================================

#define BUZZER 3

const int leds[] = {4,5,6,7,8,9,10,11,12,13};
const int NUM_LEDS = 10;

// -------- Musical Notes --------
#define C4 262
#define D4 294
#define E4 330
#define F4 349
#define G4 392
#define A4 440
#define B4 494

#define C5 523
#define D5 587
#define E5 659
#define F5 698
#define G5 784

// -------- Happy Birthday Melody --------
int melody[] = {
  G4,G4,A4,G4,C5,B4,
  G4,G4,A4,G4,D5,C5,
  G4,G4,G5,E5,C5,B4,A4,
  F5,F5,E5,C5,D5,C5
};

int duration[] = {
  4,8,4,4,4,2,
  4,8,4,4,4,2,
  4,8,4,4,4,4,2,
  4,8,4,4,4,2
};

void setup()
{
  pinMode(BUZZER, OUTPUT);

  for(int i=0;i<NUM_LEDS;i++)
  {
    pinMode(leds[i],OUTPUT);
    digitalWrite(leds[i],LOW);
  }
}

void loop()
{
  int ledPos = 0;

  for(int i=0;i<25;i++)
  {
    int noteTime = 1000 / duration[i];

    tone(BUZZER, melody[i], noteTime);

    scanner(ledPos);

    ledPos++;
    if(ledPos>=NUM_LEDS)
      ledPos=0;

    delay(noteTime*1.35);

    noTone(BUZZER);
  }

  celebration();

  delay(3000);
}

void scanner(int pos)
{
  for(int i=0;i<NUM_LEDS;i++)
    digitalWrite(leds[i],LOW);

  digitalWrite(leds[pos],HIGH);

  if(pos>0)
    digitalWrite(leds[pos-1],HIGH);

  if(pos<NUM_LEDS-1)
    digitalWrite(leds[pos+1],HIGH);
}

void celebration()
{
  for(int j=0;j<15;j++)
  {
    // Even LEDs
    for(int i=0;i<NUM_LEDS;i++)
      digitalWrite(leds[i], (i%2==0));

    tone(BUZZER,900,80);
    delay(100);

    // Odd LEDs
    for(int i=0;i<NUM_LEDS;i++)
      digitalWrite(leds[i], (i%2==1));

    tone(BUZZER,1200,80);
    delay(100);
  }

  // Chase Effect
  for(int k=0;k<4;k++)
  {
    for(int i=0;i<NUM_LEDS;i++)
    {
      for(int j=0;j<NUM_LEDS;j++)
        digitalWrite(leds[j],LOW);

      digitalWrite(leds[i],HIGH);

      tone(BUZZER,500+i*60,50);

      delay(60);
    }
  }

  // All Blink
  for(int i=0;i<8;i++)
  {
    for(int j=0;j<NUM_LEDS;j++)
      digitalWrite(leds[j],HIGH);

    tone(BUZZER,1000,120);

    delay(150);

    for(int j=0;j<NUM_LEDS;j++)
      digitalWrite(leds[j],LOW);

    delay(150);
  }
}