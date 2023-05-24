#include <wiringPi.h>
#include <stdio.h>
#include <time.h>

// NPN NO: 常态下常开，检测到物体时输出负电压

#define PIN      13
#define REDLED   9
#define BLUELED  8
#define GREENLED 10

#define OBSTACLE 0

int main(int argc, char *argv[])
{
    printf("main run\n");
    if(wiringPiSetup() == -1) {
        printf("setup of wiringPi failed !\n");
        return 1;
    }

    pinMode(REDLED, OUTPUT);
    pinMode(BLUELED, OUTPUT);
    pinMode(GREENLED, OUTPUT);
	pinMode(PIN, INPUT);
    printf("--> %d\n", digitalRead(BLUELED));
    int count = 0;
    while (1) {
        if (OBSTACLE == digitalRead(PIN)) {
            while (OBSTACLE == digitalRead(PIN)) delay(200);
            count++;
            printf("count = %d\n", count);
        }
        delay(200);
    }
    return 0;
}
