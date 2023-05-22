#include <stdio.h>
#include <wiringPi.h>

#define PIR_PIN 13

void motionDetected(void)
{
    printf("Motion detected!\n");
}

int main(void) {
    wiringPiSetup();

    pinMode(PIR_PIN, INPUT);

    wiringPiISR(PIR_PIN, INT_EDGE_FALLING, &motionDetected);

    printf("PIR Motion Sensor Example\n");
    printf("Press Ctrl+C to exit\n");

    while (1) {
        // Keep the program running
    }

    return 0;
}
