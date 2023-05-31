#include <wiringPi.h>
#include <stdio.h>
#include <time.h>
#include <pthread.h>

#define BTNPIN   2
#define TSKPIN   13

#define REDLED   9
#define BLUELED  8
#define GREENLED 10

#define BTN_ONPRESS 0
#define BTN_RELEASE 1

#define TASK_NONE      0
#define TASK_PHOTOELE  1
#define TASK_MAGNETSW  2
#define TASK_VIBRATSW  3
#define TASK_PIR       4

// R G B
int black[]   = {0, 0, 0};
int red[]     = {1, 0, 0};
int green[]   = {0, 1, 0};
int blue[]    = {0, 0, 1};
int yellow[]  = {1, 1, 0};
int cyan[]    = {0, 1, 1};
int magenta[] = {1, 0, 1};
int white[]   = {1, 1, 1};

static pthread_t thread_id;
static pthread_mutex_t task_mutex;
static int g_current_task = TASK_NONE;
static int *g_current_color = (int*)black;

static void init()
{
    pinMode(BTNPIN, INPUT);
    pinMode(REDLED, OUTPUT);
    pinMode(BLUELED, OUTPUT);
    pinMode(GREENLED, OUTPUT);
}


static void switch_to(const int rgb[3])
{
    digitalWrite(REDLED   , rgb[0]);
    digitalWrite(GREENLED , rgb[1]);
    digitalWrite(BLUELED  , rgb[2]);
}


static void do_photoelectric(int task)
{
    fprintf(stderr, "do_photoelectric");
	pinMode(TSKPIN, INPUT);
    int count = 0;
    while (g_current_task == task) {
        if (0 == digitalRead(TSKPIN)) {
            switch_to(black);
            while (g_current_task == task && 0 == digitalRead(TSKPIN)) delay(200);
            switch_to(g_current_color);
            count++;
            printf("count = %d\n", count);
        }
        delay(200);
    }
}


static void do_vibration_switch(int task)
{
    fprintf(stderr, "do_vibration_switch");
    pinMode(TSKPIN, INPUT);
    const int threshold = 200; // ms
    int value = 0, count = 0;
    int sumtimer = 0;
    while (g_current_task == task) {
        value = digitalRead(TSKPIN);
        if (1 == value) { // vibrate
            sumtimer = 0;
            switch_to(black);
            do {
                if (value == digitalRead(TSKPIN))
                    sumtimer = 0;
                else
                    sumtimer += 20;
                delay(20);
                printf("sumtimer = %d\n", sumtimer);
            } while(g_current_task == task && sumtimer < threshold);
            switch_to(g_current_color);
            count++;
            printf("count = %d\n", count);
        }
        delay(200);
    }
}


static void do_vibration_switch_2(int task)
{
    fprintf(stderr, "do_vibration_switch2");
    pinMode(TSKPIN, INPUT);
    const int threshold = 200; // ms
    int value = 0, count = 0;
    int sumtimer = 0;
    while (g_current_task == task) {
        value = digitalRead(TSKPIN);
        if (0 == value) { // vibrate
            sumtimer = 0;
            switch_to(black);
            do {
                if (value == digitalRead(TSKPIN))
                    sumtimer = 0;
                else
                    sumtimer += 20;
                delay(20);
                printf("sumtimer = %d\n", sumtimer);
            } while(g_current_task == task && sumtimer < threshold);
            switch_to(g_current_color);
            count++;
            printf("count = %d\n", count);
        }
        delay(20);
    }
}


static void do_passive_infrared_detect(int task)
{
    fprintf(stderr, "do_passive_infrared_detect");
    pinMode(TSKPIN, INPUT);
    int count = 0;
    int current_state = 0, previous_state = -1; // 0: detected 1: no detected
    while (g_current_task == task) {
        current_state = digitalRead(TSKPIN);
        printf("%d\n", current_state);
        if (current_state != previous_state) {
            if (0 == current_state) {
                // motion detect
                switch_to(g_current_color);
            } else {
                switch_to(black);
                count ++;
                printf("count = %d\n", count);
            }
            previous_state = current_state;
        }
        delay(200);
    }
}


static void do_passive_infrared_detect_2(int task)
{
    fprintf(stderr, "do_passive_infrared_detect_2");
    pinMode(TSKPIN, INPUT);
    int count = 0;
    time_t pre_time = time(0), cur_time = -1;
    int current_state = 0, previous_state = -1; // 1: detected 0: no detected
    while (g_current_task == task) {
        current_state = digitalRead(TSKPIN);
        if (current_state != previous_state) {
            if (1 == current_state) {
                pre_time = time(0);
                // motion detect
                switch_to(g_current_color);
            } else {
                cur_time = time(0);
                switch_to(black);
                count ++;
                printf("count = %d %ld %ld\n", count, cur_time, cur_time - pre_time);
                pre_time = cur_time;
            }
            previous_state = current_state;
        }
        delay(500);
    }
}


static void *loop_task(void *arg)
{
    while (1) {
        pthread_mutex_lock(&task_mutex);
        int task = g_current_task;
        pthread_mutex_unlock(&task_mutex);
        switch (task) {
            case TASK_NONE:
                break;
            case TASK_PHOTOELE:
            case TASK_MAGNETSW:
                do_photoelectric(task);
                break;
            case TASK_VIBRATSW:
                do_passive_infrared_detect_2(task);
                // do_vibration_switch(task);
                break;
            case TASK_PIR:
                do_passive_infrared_detect(task);
                break;
        }
        delay(500);
    }
    return 0;
}

void schedule_task(int duration, int boot)
{
    // printf("schedule duration: %d\n", duration);
    if (1 == boot)
        pthread_mutex_lock(&task_mutex);
    switch (duration) {
        case 0:
            switch_to(blue);
            if (1 == boot) {
                g_current_task = TASK_VIBRATSW;
                g_current_color = (int*)blue;
            }
            break;
        case 1:
        case 2:
            switch_to(red);
            if (1 == boot) {
                g_current_task = TASK_PHOTOELE;
                g_current_color = (int*)red;
            }
            break;
        case 3:
        case 4:
        case 5:
            switch_to(green);
            if (1 == boot) {
                g_current_task = TASK_MAGNETSW;
                g_current_color = (int*)green;
            }
            break;
        case 6:
        case 7:
        case 8:
            switch_to(blue);
            if (1 == boot) {
                g_current_task = TASK_VIBRATSW;
                g_current_color = (int*)blue;
            }
            break;
        case 9:
        case 10:
        case 11:
            switch_to(yellow);
            if (1 == boot) {
                g_current_task = TASK_PIR;
                g_current_color = (int*)yellow;
            }
            break;
        case 12:
        case 13:
        case 14:
            switch_to(cyan);
            break;
        case 15:
        case 16:
        case 17:
            switch_to(magenta);
            break;
        default:
            switch_to(black);
            if (1 == boot) {
                g_current_task = TASK_NONE;
                g_current_color = (int*)black;
                printf("duration:%d not catch\n", duration);
            }
    }
    if (1 == boot)
        pthread_mutex_unlock(&task_mutex);
}


int main(int argc, char *argv[])
{
    fprintf(stderr, "main run");
    if(wiringPiSetup() == -1) {
        printf("setup of wiringPi failed !\n");
        return 1;
    }

    init();
    switch_to(black);

    pthread_create(&thread_id, NULL, loop_task, NULL);

    time_t press_timer = time(0);
    int btnvalue = BTN_RELEASE, duration = 0;
    schedule_task(0, 0);
    schedule_task(0, 1);
    while (1) {
        duration = 0;
        btnvalue = digitalRead(BTNPIN);
        if (btnvalue == BTN_ONPRESS) {
            press_timer = time(0);
            while (BTN_ONPRESS == digitalRead(BTNPIN)) {
                duration = time(0) - press_timer;
                schedule_task(duration, 0);
                delay(10);
            }
            schedule_task(duration, 1);
        }
        delay(500);
    }

    return 0;
}
