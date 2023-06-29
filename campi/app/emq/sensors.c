/******************************************************************************
* File:             sensors.c
*
* Author:
* Created:          06/06/23
* Description:
*****************************************************************************/

#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <wiringPi.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <syslog.h>

#include "cjson/cJSON.h"

#include "emqc.h"

#define MAX_BUF  1024
#define BTNPIN   2    // PC9
#define TSKPIN   6    // PC11

#define REDLED   5    // PC6
#define GREENLED 7    // PC5
#define BLUELED  8    // PC8

#define BTN_ONPRESS 0
#define BTN_RELEASE 1

#define SENSOR_CONFIG "/campi/runtime/campi_sensor.json"
#define PIEMQ_FIFO    "/tmp/emq_sensor.fifo"

extern int sensor_init(const char*);
extern void sensor_detect();
extern int syscall_exec(const char* cmd);

enum {
    COLOR_WHITE = 0,
    COLOR_RED,         // SENSOR_VIBRATSW
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    COLOR_CYAN,
    COLOR_MAGENTA,
    COLOR_BLACK,
};

enum {
    SENSOR_UNIVERSAL,  // COLOR_WHITE
    SENSOR_VIBRATSW,   // COLOR_RED
    SENSOR_PIR,        // COLOR_GREEN
    SENSOR_PHOTOELE,   // COLOR_BLUE
    SENSOR_MAGNETSW    // COLOR_YELLOW
};

static char SENSOR_NAMES[][16] = {
    "universal",
    "vibratsw",
    "pir",
    "photoele",
    "magnetsw",
};

static char SENSOR_TOPIC[64] = { 0 };

static int _RGB[8][3] = {
    {1, 1, 1},  // white
    {1, 0, 0},
    {0, 1, 0},
    {0, 0, 1},
    {1, 1, 0},  // yellow
    {0, 1, 1},
    {1, 0, 1},
    {0, 0, 0},  // black
};

static int g_fifo_w = -1;
static pthread_t g_thread_id;
static pthread_mutex_t g_mutex;

static int g_thresh_quiet = 500;

static int g_sensor_debug = 0;
static int g_current_color = COLOR_WHITE;
static int g_current_sensor = SENSOR_UNIVERSAL;
static int g_repeat_counter = 0;
static int g_trigger_pulse = 1;
static int g_calm_step_ms = 20;
static int g_calm_down_ms = 200;
static int g_read_sleep_ms = 300;


void _sensor_parse_config(const char* config)/*{{{*/
{
    cJSON* cjson = cJSON_Parse(config);
    if (cjson == NULL) {
        syslog(LOG_ERR, "cjson parse error!\n");
        return;
    }
    cJSON* jcount = cJSON_GetObjectItem(cjson, "count");
    if (cJSON_IsNumber(jcount))
        g_repeat_counter = jcount->valueint;
    cJSON* jccolor = cJSON_GetObjectItem(cjson, "current_color");
    if (cJSON_IsNumber(jccolor)) {
        g_current_color = jccolor->valueint;
    }
    cJSON* jcsensor = cJSON_GetObjectItem(cjson, "current_sensor");
    if (cJSON_IsNumber(jcsensor))
        g_current_sensor = jcsensor->valueint;
    cJSON* jtrigger_pulse = cJSON_GetObjectItem(cjson, "trigger_pulse");
    if (cJSON_IsNumber(jtrigger_pulse))
        g_trigger_pulse = jtrigger_pulse->valueint;
    cJSON* jcaml_step = cJSON_GetObjectItem(cjson, "calm_step_ms");
    if (cJSON_IsNumber(jcaml_step))
        g_calm_step_ms = jcaml_step->valueint;
    cJSON* jcaml_down = cJSON_GetObjectItem(cjson, "calm_down_ms");
    if (cJSON_IsNumber(jcaml_down))
        g_calm_down_ms = jcaml_down->valueint;
    cJSON* jread_sleep = cJSON_GetObjectItem(cjson, "read_sleep_ms");
    if (cJSON_IsNumber(jread_sleep))
        g_read_sleep_ms = jread_sleep->valueint;
    cJSON_Delete(cjson);
}/*}}}*/

const char* _sensor_get_config(char* config, int size, const char* extra)/*{{{*/
{
    char buff[MAX_BUF] = { 0 };
    snprintf(buff, size,
             "\"current_color\": %d, \"current_sensor\": %d, \"sensor\": \"%s\", \"count\": %d, \"trigger_pulse\": %d, \"calm_step_ms\": %d, \"calm_down_ms\": %d, \"read_sleep_ms\": %d",
             g_current_color, g_current_sensor, SENSOR_NAMES[g_current_sensor], g_repeat_counter, g_trigger_pulse, g_calm_step_ms, g_calm_down_ms, g_read_sleep_ms);
    if (NULL != extra)
        snprintf(buff + strlen(buff), MAX_BUF, ", %s", extra);
    memset(config, 0, size);
    snprintf(config, size, "{%s}", buff);
    return config;
}/*}}}*/

static void _save_current_state()/*{{{*/
{
    int fd = open(SENSOR_CONFIG, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) {
        syslog(LOG_ERR, "write file %s error\n", SENSOR_CONFIG);
        exit(-1);
    }
    char config[MAX_BUF] = { 0 };
    _sensor_get_config(config, MAX_BUF, NULL);
    int sz = write(fd, config, strlen(config));
    syslog(LOG_DEBUG, "[%d] save state %s\n", sz, config);
    close(fd);
}/*}}}*/

static void _load_current_state()/*{{{*/
{
    int fd = open(SENSOR_CONFIG, O_RDONLY | O_CREAT, 0644);
    if (fd < 0) {
        syslog(LOG_ERR, "read file %s error\n", SENSOR_CONFIG);
        exit(-1);
    }
    char buff[MAX_BUF] = { 0 };
    int sz = read(fd, buff, MAX_BUF);
    if (sz > 0) {
        _sensor_parse_config(buff);
        syslog(LOG_DEBUG, "[%d] load state %s\n", sz, buff);
    }
    close(fd);
}/*}}}*/

static void _change_color_to(int c)/*{{{*/
{
    digitalWrite(REDLED   , _RGB[c][0]);
    digitalWrite(GREENLED , _RGB[c][1]);
    digitalWrite(BLUELED  , _RGB[c][2]);
}/*}}}*/

static void _change_sensor_to(int c, int s)/*{{{*/
{
    if (s != g_current_sensor) {
        pthread_mutex_lock(&g_mutex);
        g_current_color = c;
        g_current_sensor = s;
        g_repeat_counter = 0;
        pthread_mutex_unlock(&g_mutex);
        _save_current_state();
    }
}/*}}}*/

void _emq_report(const char* extra)/*{{{*/
{
    char payload[MAX_BUF] = { 0 };
    snprintf(payload, MAX_BUF, "%d\n", g_repeat_counter);
    if (write(g_fifo_w, payload, strlen(payload)) > 0) {
    }
    _sensor_get_config(payload, MAX_BUF, extra);
    emqc_pub(SENSOR_TOPIC, payload);
    syslog(LOG_DEBUG, "pub [%s]: %s\n", SENSOR_TOPIC, payload);
}/*}}}*/

void _emq_on_message(const char* topic, const char* payload)/*{{{*/
{
    syslog(LOG_DEBUG, "receive [%s]: %s\n", topic, payload);
    _sensor_parse_config(payload);
    _save_current_state();
}/*}}}*/

static void _sensor_common_task(int s)/*{{{*/
{
    int value, sumtimer;
    char buff[64] = { 0 };
    while (g_current_sensor == s) {
        value = digitalRead(TSKPIN);
        if (g_trigger_pulse == value) {
            _change_color_to(g_current_color);
            sumtimer = 0;
            do {
                if (value == digitalRead(TSKPIN))
                    sumtimer = 0;
                else
                    sumtimer += g_calm_step_ms;
                delay(g_calm_step_ms);
            } while(g_current_sensor == s && sumtimer < g_calm_down_ms);
            g_repeat_counter += 1;
            _change_color_to(COLOR_BLACK);
            _emq_report(NULL);
        }
        delay(g_read_sleep_ms);
    }
}/*}}}*/

static void _sensor_vibration_switch(int s)/*{{{*/
{
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
            g_repeat_counter += 1;
            _change_color_to(g_current_color);
            _emq_report(NULL);
        }
        delay(200);
    }
}/*}}}*/

static void _sensor_passive_infrared(int s)/*{{{*/
{
    syslog(LOG_DEBUG, "sensor passive infrared detection\n");
    pinMode(TSKPIN, INPUT);
    int value = 0, sumtimer = 0;
    char buff[64] = { 0 };
    int thresh_quiet = 3500;
    while (g_current_sensor == s) {
        value = digitalRead(TSKPIN);
        if (0 == value) { // motion detect
            sumtimer = 0;
            _change_color_to(g_current_color);
            do {
                if (value == digitalRead(TSKPIN))
                    sumtimer = 0;
                else
                    sumtimer += 100;
                delay(100);
            } while(g_current_sensor == s && sumtimer < thresh_quiet);
            g_repeat_counter += 1;
            _change_color_to(COLOR_BLACK);
            _emq_report(NULL);
        }
        delay(500);
    }
}/*}}}*/

static void _sensor_photoelectric_or_magnet(int s)/*{{{*/
{
    syslog(LOG_DEBUG, "sensor photo electirc or magnat\n");
	pinMode(TSKPIN, INPUT);
    while (g_current_sensor == s) {
        if (0 == digitalRead(TSKPIN)) {
            _change_color_to(COLOR_BLACK);
            while (g_current_sensor == s && 0 == digitalRead(TSKPIN)) delay(200);
            _change_color_to(g_current_color);
            g_repeat_counter++;
            _emq_report(NULL);
        }
        delay(200);
    }
}/*}}}*/

static void *_sensor_worker(void *arg)
{/*{{{*/
    while (1) {
        pthread_mutex_lock(&g_mutex);
        int s = g_current_sensor;
        pthread_mutex_unlock(&g_mutex);
        switch (s) {
            case SENSOR_UNIVERSAL:
                _sensor_common_task(s);
                break;
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

    if (0 != access(PIEMQ_FIFO, F_OK))
        mkfifo(PIEMQ_FIFO, 0666);
    g_fifo_w = open(PIEMQ_FIFO, O_RDWR | O_NONBLOCK);
    if (g_fifo_w < 0) {
        syslog(LOG_ERR, "open fifo %s error\n", PIEMQ_FIFO);
        exit(1);
    }

    if(wiringPiSetup() == -1) {
        syslog(LOG_ERR, "setup of wiringPi failed !\n");
        exit(1);
    }

    pinMode(BTNPIN, INPUT);
    pinMode(REDLED, OUTPUT);
    pinMode(BLUELED, OUTPUT);
    pinMode(GREENLED, OUTPUT);

    pthread_create(&g_thread_id, NULL, _sensor_worker, NULL);
    _load_current_state();
    _change_color_to(g_current_color);

    snprintf(SENSOR_TOPIC, sizeof(SENSOR_TOPIC) - 1, "campi/%s/sensor/report", client_id);
    char buff[64] = {0};
    snprintf(buff, 63, "cloud/%s/sensor/config", client_id);
    emqc_sub(buff, _emq_on_message);
    return 0;
}/*}}}*/

// static time_t short_press_count = 0;
// static time_t btnon_press_timer = 0;
// static time_t curr_release_timer = 0;
// static time_t prev_release_timer = 0;

void sensor_detect()
{/*{{{*/
    if (BTN_RELEASE == digitalRead(BTNPIN)) {
        // curr_release_timer = time(0);
        // time_t interval = curr_release_timer - prev_release_timer;
        // if (interval < 1) {
        //     short_press_count++;
        //     prev_release_timer = curr_release_timer;
        // } else if (interval > 2) {
        //     if (short_press_count > 1) {
        //         switch (short_press_count) {
        //             case 2: {
        //                 break;
        //             }
        //             case 3: {
        //                 syscall_exec("systemctl start campi_frp.service");
        //                 break;
        //             }
        //             default: break;
        //         }
        //     }
        // }
        return;
    }

    int duration = 0, color = COLOR_BLACK;
    time_t press_timer = time(0);
    while (BTN_ONPRESS == digitalRead(BTNPIN)) {
        duration = time(0) - press_timer;

        switch (duration) {
            case 0: color = COLOR_WHITE; break;
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
            default: color = COLOR_BLACK;
        }
        _change_color_to(color);
        delay(20);
    }
    switch (color) {
        case COLOR_WHITE: {
            _change_sensor_to(color, SENSOR_UNIVERSAL);
            break;
        }
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
            _change_sensor_to(color, SENSOR_UNIVERSAL);
            break;
        }
    }
    delay(200);
}/*}}}*/
