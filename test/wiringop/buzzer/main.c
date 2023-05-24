#include <wiringPi.h>
#include <stdio.h>

#define BUZZERPIN 13

int main()
{
    if(wiringPiSetup() == -1) {
        printf("setup wiringPi failed !");
        return 1;
    }

    pinMode(BUZZERPIN, OUTPUT);
    while(1) {
        digitalWrite(BUZZERPIN, LOW);
        delay(2000);
        digitalWrite(BUZZERPIN, HIGH);
        delay(2000);
    }
    return 0;
}
