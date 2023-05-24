#include <wiringPi.h>
#include <stdio.h>
#include <time.h>

#define BtnPin      2
#define Gpin        10
#define Rpin        9

#define RED     1
#define GREEN   2

void LED(int color)
{
    pinMode(Gpin, OUTPUT);
    pinMode(Rpin, OUTPUT);
    if (color == RED)
    {
        digitalWrite(Rpin, HIGH);
        digitalWrite(Gpin, LOW);
    }
    else if (color == GREEN)
    {
        digitalWrite(Rpin, LOW);
        digitalWrite(Gpin, HIGH);
    }
    else
        printf("LED Error");
}


int main(void)
{
    if(wiringPiSetup() == -1){ //when initialize wiring failed,print messageto screen
        printf("setup wiringPi failed !");
        return 1;
    }

    pinMode(BtnPin, INPUT);
    LED(GREEN);

    while(1){
        if(0 == digitalRead(BtnPin)){
            delay(10);
            if(0 == digitalRead(BtnPin)){
                LED(RED);
                printf("Button is pressed\n");
            }
        }
        else if(1 == digitalRead(BtnPin)){
            delay(10);
            if(1 == digitalRead(BtnPin)){
                LED(GREEN);
                printf("Button is released\n");
            }
        }
    }
    return 0;
}
