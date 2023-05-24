#include <stdio.h>
#include <time.h>
#include <wiringPi.h>

#define PIR_PIN 13

time_t timer;

void motionDetected(void)
{
    int duration = time(NULL) - timer;
    printf("Motion detected! %d\n", duration);
    timer = time(NULL);
}

int main(void) 
{
    wiringPiSetup();

    pinMode(PIR_PIN, INPUT);

    timer = time(NULL);
    // wiringPiISR(PIR_PIN, INT_EDGE_FALLING, &motionDetected);
    wiringPiISR(PIR_PIN, INT_EDGE_RISING, &motionDetected);

    printf("PIR Motion Sensor Example\n");
    printf("Press Ctrl+C to exit\n");

    while (1) {
        // Keep the program running
    }

    return 0;
}
