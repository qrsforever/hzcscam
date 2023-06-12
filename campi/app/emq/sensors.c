/******************************************************************************
* File:             sensors.c
*
* Author:
* Created:          06/06/23
* Description:
*****************************************************************************/

#include <stdlib.h>
#include <string.h>
#include <wiringPi.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <syslog.h>

#include "cjson/cJSON.h"

#include "emqc.h"

#define BTNPIN   2    // PC9
#define TSKPIN   6    // PC11

#define REDLED   5    // PC6
#define GREENLED 7    // PC5
#define BLUELED  8    // PC8

#define BTN_ONPRESS 0
#define BTN_RELEASE 1

#define STATE_FILE   "/campi/runtime/emq_sensor.state"

extern int sensor_init(const char*);
extern void sensor_detect();

enum {
    COLOR_BLACK = 0,
    COLOR_RED,
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    COLOR_CYAN,
    COLOR_MAGENTA,
    COLOR_WHITE
};

enum {
    SENSOR_NONE = 0,
    SENSOR_VIBRATSW,
    SENSOR_PIR,
    SENSOR_PHOTOELE,
    SENSOR_MAGNETSW
};

static char SENSOR_NAMES[][16] = {
    "none",
    "vibratsw",
    "pir",
    "photoele",
    "magnetsw",
};

static char SENSOR_TOPIC[64] = { 0 };


static int _RGB[8][3] = {
    {0, 0, 0},  // black
    {1, 0, 0},
    {0, 1, 0},
    {0, 0, 1},
    {1, 1, 0},  // yellow
    {0, 1, 1},
    {1, 0, 1},
    {1, 1, 1},  // white
};

static pthread_t g_thread_id;
static pthread_mutex_t g_mutex;
static int g_current_color = COLOR_RED;
static int g_current_sensor = SENSOR_VIBRATSW;
static unsigned int g_repeat_count = 0;
static unsigned int g_thresh_quiet = 200;


void _emq_report(const char* extra)
{
    char payload[256] = { 0 };
    if (extra == NULL) {
        snprintf(
            payload, 255,
            "{\"count\": %d, \"sensor\": \"%s\"}",
            g_repeat_count,
            SENSOR_NAMES[g_current_sensor]);
    } else {
        snprintf(
            payload, 255,
            "{\"count\": %d, \"sensor\": \"%s\", %s}",
            g_repeat_count,
            SENSOR_NAMES[g_current_sensor], extra);
    }

    emqc_pub(SENSOR_TOPIC, payload);
    syslog(LOG_DEBUG, "pub [%s]: %s\n", SENSOR_TOPIC, payload);
}

void _emq_on_message(const char* topic, const char* payload)
{/*{{{*/
    syslog(LOG_DEBUG, "receive [%s]: %s\n", topic, payload);
    cJSON* cjson = cJSON_Parse(payload);
    if (cjson == NULL) {
        syslog(LOG_ERR, "cjson parse error!\n");
        return;
    }
    cJSON* jcount = cJSON_GetObjectItem(cjson, "count");
    if (cJSON_IsNumber(jcount))
        g_repeat_count = jcount->valueint;
    cJSON* jthres = cJSON_GetObjectItem(cjson, "threshold");
    if (cJSON_IsNumber(jthres))
        g_thresh_quiet = jthres->valueint;
    cJSON_Delete(cjson);
}/*}}}*/

static void _save_current_state()
{/*{{{*/
    int fd = open(STATE_FILE, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        syslog(LOG_ERR, "write file %s error\n", STATE_FILE);
        exit(-1);
    }
    char buff[8] = { 0 };
    sprintf(buff, "%d,%d", g_current_color, g_current_sensor);
    int sz = write(fd, buff, strlen(buff));
    syslog(LOG_DEBUG, "[%d] save state %d %d\n", sz, g_current_color, g_current_sensor);
    close(fd);
}/*}}}*/

static void _load_current_state()
{/*{{{*/
    int fd = open(STATE_FILE, O_RDONLY | O_CREAT, 0644);
    if (fd < 0) {
        syslog(LOG_ERR, "read file %s error\n", STATE_FILE);
        exit(-1);
    }
    char buff[8] = { 0 };
    int sz =read(fd, buff, 8);
    if (sz > 0) {
        sscanf(buff, "%d,%d", &g_current_color, &g_current_sensor);
        syslog(LOG_DEBUG, "[%d] load state %d %d\n", sz, g_current_color, g_current_sensor);
    }
    close(fd);
}/*}}}*/

static void _change_color_to(int c)
{/*{{{*/
    digitalWrite(REDLED   , _RGB[c][0]);
    digitalWrite(GREENLED , _RGB[c][1]);
    digitalWrite(BLUELED  , _RGB[c][2]);
}/*}}}*/

static void _change_sensor_to(int c, int s)
{/*{{{*/
    if (s != g_current_sensor) {
        pthread_mutex_lock(&g_mutex);
        g_current_color = c;
        g_current_sensor = s;
        g_repeat_count = 0;
        pthread_mutex_unlock(&g_mutex);
        _save_current_state();
    }
}/*}}}*/

static void _sensor_vibration_switch(int s)
{/*{{{*/
    syslog(LOG_DEBUG, "sensor vibrate switch\n");
    pinMode(TSKPIN, INPUT);
    int value = 0, sumtimer = 0;
    char buff[64] = { 0 };
    while (g_current_sensor == s) {
        value = digitalRead(TSKPIN);
        if (1 == value) { // vibrate
            sumtimer = 0;
            _change_color_to(COLOR_BLACK);
            do {
                if (value == digitalRead(TSKPIN))
                    sumtimer = 0;
                else
                    sumtimer += 20;
                delay(20);
            } while(g_current_sensor == s && sumtimer < g_thresh_quiet);
            g_repeat_count += 1;
            _change_color_to(g_current_color);
            snprintf(buff, 63, "\"threshold\": %d", g_thresh_quiet);
            _emq_report(buff);
        }
        delay(200);
    }
}/*}}}*/

static void _sensor_passive_infrared(int s)/*{{{*/
{
    syslog(LOG_DEBUG, "sensor passive infrared detection\n");
    pinMode(TSKPIN, INPUT);
    int current_state = 0, previous_state = -1; // 1: detected 0: no detected
    time_t detect_time = time(0);
    char buff[64] = { 0 };
    while (g_current_sensor == s) {
        current_state = digitalRead(TSKPIN);
        if (current_state != previous_state) {
            if (1 == current_state) {
                // motion detect
                detect_time = time(0);
                _change_color_to(g_current_color);
            } else {
                g_repeat_count += 1;
                _change_color_to(COLOR_BLACK);
                snprintf(buff, 63, "{\"stay_time\": %ld}", time(0) - detect_time);
                _emq_report(buff);
            }
            previous_state = current_state;
        }
        delay(500);
    }
}
/*}}}*/
static void _sensor_photoelectric_or_magnet(int s)
{
    syslog(LOG_DEBUG, "sensor photo electirc or magnat\n");
	pinMode(TSKPIN, INPUT);
    while (g_current_sensor == s) {
        if (0 == digitalRead(TSKPIN)) {
            _change_color_to(COLOR_BLACK);
            while (g_current_sensor == s && 0 == digitalRead(TSKPIN)) delay(200);
            _change_color_to(g_current_color);
            g_repeat_count++;
            _emq_report(NULL);
        }
        delay(200);
    }
}

static void *_sensor_worker(void *arg)
{/*{{{*/
    while (1) {
        pthread_mutex_lock(&g_mutex);
        int s = g_current_sensor;
        pthread_mutex_unlock(&g_mutex);
        switch (s) {
            case SENSOR_VIBRATSW:
                _sensor_vibration_switch(s);
                break;
            case SENSOR_PIR:
                _sensor_passive_infrared(s);
                break;
            case SENSOR_PHOTOELE:
            case SENSOR_MAGNETSW:
                _sensor_photoelectric_or_magnet(s);
                break;
            default:
                break;
        }
        delay(1000);
    }
    return 0;
}/*}}}*/

int sensor_init(const char* client_id)
{/*{{{*/
    syslog(LOG_DEBUG, "sensor_init\n");
    if(wiringPiSetup() == -1) {
        syslog(LOG_ERR, "setup of wiringPi failed !\n");
        return -1;
    }

    pinMode(BTNPIN, INPUT);
    pinMode(REDLED, OUTPUT);
    pinMode(BLUELED, OUTPUT);
    pinMode(GREENLED, OUTPUT);

    pthread_create(&g_thread_id, NULL, _sensor_worker, NULL);
    _load_current_state();
    _change_color_to(g_current_color);

    char buff[64] = {0};
    snprintf(buff, 63, "cloud/%s/sensors/set", client_id);
    emqc_sub(buff, _emq_on_message);
    snprintf(SENSOR_TOPIC, sizeof(SENSOR_TOPIC) - 1, "campi/%s/sensors/put", client_id);
    return 0;
}/*}}}*/

void sensor_detect()
{/*{{{*/
    int duration = 0, color = COLOR_BLACK;
    if (BTN_RELEASE == digitalRead(BTNPIN))
        return;

    time_t press_timer = time(0);
    while (BTN_ONPRESS == digitalRead(BTNPIN)) {
        duration = time(0) - press_timer;

        switch (duration) {
            case 0: color = COLOR_BLACK; break;
            case 1:
            case 2: color = COLOR_RED; break;
            case 3:
            case 4: color = COLOR_GREEN; break;
            case 5:
            case 6: color = COLOR_BLUE; break;
            case 7:
            case 8: color = COLOR_YELLOW; break;
            case 9:
            case 10: color = COLOR_CYAN; break;
            case 11:
            case 12: color = COLOR_MAGENTA; break;
            default: color = COLOR_WHITE;
        }
        _change_color_to(color);
        delay(10);
    }
    switch (color) {
        case COLOR_RED: {
            _change_sensor_to(color, SENSOR_VIBRATSW);
            break;
        }
        case COLOR_GREEN: {
            _change_sensor_to(color, SENSOR_PIR);
            break;
        }
        case COLOR_BLUE: {
            _change_sensor_to(color, SENSOR_PHOTOELE);
            break;
        }
        case COLOR_YELLOW: {
            _change_sensor_to(color, SENSOR_MAGNETSW);
            break;
        }
        default: {
            _change_sensor_to(color, SENSOR_NONE);
            break;
        }
    }
    delay(200);
}/*}}}*/
