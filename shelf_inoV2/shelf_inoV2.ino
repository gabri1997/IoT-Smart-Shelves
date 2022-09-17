#include <FastIO.h>
#include <I2CIO.h>
#include <LCD.h>
#include <LiquidCrystal.h>
#include <LiquidCrystal_I2C.h>
#include <LiquidCrystal_I2C_ByVac.h>
#include <LiquidCrystal_SI2C.h>
#include <LiquidCrystal_SR.h>
#include <LiquidCrystal_SR1W.h>
#include <LiquidCrystal_SR2W.h>
#include <LiquidCrystal_SR3W.h>
#include <SI2CIO.h>
#include <SoftI2CMaster.h>

#include <Wire.h> 

#define I2C_ADDR 0x27 
#define BACKLIGHT_PIN 3
#define En_pin 2
#define Rw_pin 1
#define Rs_pin 0
#define D4_pin 4
#define D5_pin 5
#define D6_pin 6
#define D7_pin 7

LiquidCrystal_I2C lcd(I2C_ADDR,En_pin,Rw_pin,Rs_pin,D4_pin,D5_pin,D6_pin,D7_pin);

// Questo cambia per ogni scaffale (arduino)
// B01: scaffale di Gabriele
// H02: scaffale di Filippo
char id_shelf[4] = "H02";

// variabili globali
int s1,s2,s3;  //Il valore letto dalle fotoresistenze
char letture[3]; //array per tenere conto degli oggetti
long timer = 0; // timer per gestire i tempi
long timer_delay = 2000;  

//variabili per settaggio pin
int ledGreen = 3;  //Il pin del led verde
int ledYellow = 4;  //Il pin del led giallo
int ledRed = 5;  //Il pin del led rosso


//Variabili di stato
int count; //quanti sono oscurati
int iStateOld;
int iStateNow;

char iReceived;
char iLastReceived;

void setup() {
  Serial.begin(9600);
  pinMode(ledGreen, OUTPUT);
  pinMode(ledYellow, OUTPUT);
  pinMode(ledRed, OUTPUT);
  //settaggio parametri per usare lcd
  lcd.begin(16,2);
  lcd.setBacklightPin(BACKLIGHT_PIN,POSITIVE);
  lcd.setBacklight(HIGH);
  
  lcd.home ();    
  lcd.print("Oggetti: ");  
  lcd.setCursor(0, 1); 
  lcd.print("Prezzo: NaN");


  // serve a sapere quanta roba c'è sullo scaffale quando accendo
  read_sensors();
  iStateOld = -1;
  iLastReceived = -1;
}

void loop() {
  
  read_sensors();
  count = check();
  // controllo se possono andare a cambiare lo stato
  if((millis() - timer) > timer_delay ){
    timer = millis(); //aggiorniamo il timer
    iStateNow = computeFutureState(iStateOld, count);
    switch (iStateNow){
      case 0:
        if(iStateNow!=iStateOld){
            //scrivo sulla seriale
            Serial.write('S');
            Serial.write(id_shelf);
            Serial.write('0');
            Serial.write('P');
            Serial.flush();
        }
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledYellow, LOW);
        digitalWrite(ledRed, HIGH);
        break;
      case 1:
        if(iStateNow!=iStateOld){
            //scrivo sulla seriale
            Serial.write('S');
            Serial.write(id_shelf);
            Serial.write('1');
            Serial.write('P');
            Serial.flush();
        }
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledYellow, HIGH);
        digitalWrite(ledRed, LOW);
        break;
      case 2:
        if(iStateNow!=iStateOld){
            //scrivo sulla seriale
            Serial.write('S');
            Serial.write(id_shelf);
            Serial.write('2');
            Serial.write('P');
            Serial.flush();
        }
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledYellow, HIGH);
        digitalWrite(ledRed, LOW);
        break;
      case 3:
        if(iStateNow!=iStateOld){
            //scrivo sulla seriale
            Serial.write('S');
            Serial.write(id_shelf);
            Serial.write('3');
            Serial.write('P');
            //Serial.println("SCRIVO DA STATO 3");
            Serial.flush();
        }
        digitalWrite(ledGreen, HIGH);
        digitalWrite(ledYellow, LOW);
        digitalWrite(ledRed, LOW);
        break;
    }  
    iStateOld = iStateNow;
    lcd.setCursor(10, 0);
    lcd.print(count);
  }
  else{
      if (Serial.available() > 0){
        Serial.flush(); // Waits for the transmission of outgoing serial data to complete. 
        iReceived = Serial.read();
        if(iLastReceived != iReceived){
          // Aggiorno il dato che ho ricevuto prima con quello che ho appena ricevuto
          iLastReceived = iReceived;
          lcd.setCursor(0, 1);
          lcd.print("Prezzo:       ");
          lcd.setCursor(9, 1);
          lcd.print(iReceived);
        }
      }
  }
}


/*NUOVE FUNZIONI*/
char tipo_lettura(int lettura){
  //se il valore lettore è oscurato, quindi è presente l'oggetto
  if(lettura > 900){
    return 1;
  }
  return 0;
}

void set_letture(int s1,int s2,int s3){
    letture[0] = tipo_lettura(s1);
    letture[1] = tipo_lettura(s2);
    letture[2] = tipo_lettura(s3);
}

void read_sensors(void){
  s1 = analogRead(A0);  //Lettura della luminosità
  //Serial.print("Lettura s1: ");
  //Serial.println(s1);
  s2 = analogRead(A1);  //Lettura della luminosità
  //Serial.print("Lettura s2: ");
  //Serial.println(s2);
  s3 = analogRead(A2);  //Lettura della luminosità
  //Serial.print("Lettura s3: ");
  //Serial.println(s3);
  set_letture(s1,s2,s3);
}

int computeFutureState(int iStateOld, int count) {
  if (iStateOld == -1 && count == 0)iStateNow = 0;
  else if (iStateOld == -1 && count == 1) iStateNow = 1;
  else if (iStateOld == -1 && count == 2)iStateNow = 2;
  else if (iStateOld == -1 && count == 3)iStateNow = 3;

  else if (iStateOld == 0 && count == 0)iStateNow = 0;
  else if (iStateOld == 0 && count == 1) iStateNow = 1;
  else if (iStateOld == 0 && count == 2)iStateNow = 2;
  else if (iStateOld == 0 && count == 3)iStateNow = 3;
  // casi da stato 1
  else if (iStateOld == 1 && count == 0)iStateNow = 0;
  else if (iStateOld == 1 && count == 1) iStateNow = 1;
  else if (iStateOld == 1 && count == 2)iStateNow = 2;
  else if (iStateOld == 1 && count == 3)iStateNow = 3;
  // casi da stato 2
  else if (iStateOld == 2 && count == 0)iStateNow = 0;
  else if (iStateOld == 2 && count == 1) iStateNow = 1;
  else if (iStateOld == 2 && count == 2)iStateNow = 2;
  else if (iStateOld == 2 && count == 3)iStateNow = 3;
  // casi da stato 3
  else if (iStateOld == 3 && count == 0)iStateNow = 0;
  else if (iStateOld == 3 && count == 1) iStateNow = 1;
  else if (iStateOld == 3 && count == 2)iStateNow = 2;
  else if (iStateOld == 3 && count == 3)iStateNow = 3;

  return iStateNow;
}

int check(void){
  count = 0;
  for(int i = 0; i < 3; i++){
    if(letture[i]==1)
      count++;
  }
  //Serial.println(count);
  return count;
}
