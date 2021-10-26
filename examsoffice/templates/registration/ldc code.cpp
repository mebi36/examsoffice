#include <LiquidCrystal.h>

int rs = 2;
int en = 3;
int d4 = 4;
int d5 = 5;
int d6 = 6;
int d7 = 7;

//voltmeter parameters
int R1 = 10;
int R2 = 1;
int digitalVal;
float Vout, Vin;

//initializing our LiquidCrystal class
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);


void setup(){
    //begin the lcd pass in the columnsXrows
    lcd.begin(20,4);
    lcd.clear();


    lcd.setCursor(0,0);
    lcd.blink();
    lcd.print("Hello LCD!");


}

void loop(){
    digitalVal = analogRead(A0);
    Vout = digitalVal * 5/1023;
    Vin = ((R1 + R2)/R2) * Vout;
    
    lcd.setCursor(0,0);
    lcd.print("Vout = ");
    lcd.print(Vout);

    lcd.setCursor(0,1);
    lcd.print("Vin = ");
    lcd.print(Vin);
}