#include <wiringPi.h>
#include <stdio.h>

#define VibratePin  13
#define Gpin        10
#define Rpin        9

void LED(int color)
{
    if (color == 0)
    {
        digitalWrite(Rpin, HIGH);
        digitalWrite(Gpin, LOW);
    }
    else if (color == 1)
    {
        digitalWrite(Rpin, LOW);
        digitalWrite(Gpin, HIGH);
    }
    else
        printf("LED Error");
}

int main(void)
{
    int status = 0;
    int tmp = 1;
    int value = 1;
    if(wiringPiSetup() == -1) { //when initialize wiring failed,print messageto screen
        printf("setup wiringPi failed !");
        return 1;
    }

    pinMode(Gpin, OUTPUT);
    pinMode(Rpin, OUTPUT);
    pinMode(VibratePin, INPUT);

    while(1) {
        value = digitalRead(VibratePin);
        if (tmp != value) {
            status ++;
            if (status > 1){
                status = 0;
            }
            LED(status);
            delay(1000);
        }
    }
    return 0;
}
