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
#include <sys/syslog.h>
#include <wiringPi.h>
#include <stdio.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <syslog.h>

#include "cjson/cJSON.h"

#include "emqc.h"

#define MAX_BUF  2048
#define BTNPIN   2    // PC9
#define TSKPIN   6    // PC11

#define REDLED   5    // PC6
#define GREENLED 7    // PC5
#define BLUELED  8    // PC8

#define BTN_ONPRESS 0
#define BTN_RELEASE 1

#define SENSOR_CONFIG "/campi/runtime/emq_sensor.json"
#define PIEMQ_FIFO    "/tmp/emq_sensor.fifo"

extern int sensor_init(const char*);
extern void sensor_detect();
extern int syscall_exec(const char* cmd);

enum {
    COLOR_BLACK = 0,
    COLOR_WHITE,
    COLOR_RED,         // SENSOR_VIBRATSW
    COLOR_GREEN,
    COLOR_BLUE,
    COLOR_YELLOW,
    COLOR_CYAN,
    COLOR_MAGENTA,
};

enum {
    SENSOR_NONE = 0,
    SENSOR_UNIVERSAL,  // COLOR_WHITE
    SENSOR_VIBRATSW,   // COLOR_RED
    SENSOR_PIR,        // COLOR_GREEN
    SENSOR_PHOTOELE,   // COLOR_BLUE
    SENSOR_MAGNETSW    // COLOR_YELLOW
};

static char SENSOR_NAMES[][16] = {
    "none",
    "universal",
    "vibratsw",
    "pir",
    "photoele",
    "magnetsw",
};

static char SENSOR_TOPIC[64] = { 0 };

static int _RGB[8][3] = {
    {0, 0, 0},  // black
    {1, 1, 1},  // white
    {1, 0, 0},
    {0, 1, 0},
    {0, 0, 1},
    {1, 1, 0},  // yellow
    {0, 1, 1},
    {1, 0, 1},
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
    cJSON* jdebug = cJSON_GetObjectItem(cjson, "debug_mode");
    if (cJSON_IsNumber(jdebug))
        g_sensor_debug = jdebug->valueint;
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
             "\"debug_mode\": %d, \"current_color\": %d, \"current_sensor\": %d, \"sensor\": \"%s\", \"count\": %d, \"trigger_pulse\": %d, \"calm_step_ms\": %d, \"calm_down_ms\": %d, \"read_sleep_ms\": %d",
             g_sensor_debug, g_current_color, g_current_sensor, SENSOR_NAMES[g_current_sensor], g_repeat_counter, g_trigger_pulse, g_calm_step_ms, g_calm_down_ms, g_read_sleep_ms);
    if (NULL != extra && strlen(extra) > 0)
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
    } else {
        _save_current_state();
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
    pthread_mutex_lock(&g_mutex);
    g_current_color = c;
    g_current_sensor = s;
    g_repeat_counter = 0;
    pthread_mutex_unlock(&g_mutex);
    _save_current_state();
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

static void _sensor_universal_task(int s)/*{{{*/
{
    int value, sumtimer, len = 0;
    char buff[MAX_BUF] = { 0 };
    while (g_current_sensor == s) {
        value = digitalRead(TSKPIN);
        /*
         * trigger pulse
         * vibratsw: 1
         * pir: 0
         */
        if (g_trigger_pulse == value) {
            _change_color_to(g_current_color);
            sumtimer = 0;
            if (g_sensor_debug) {
                memset(buff, 0, MAX_BUF);
                strcpy(buff, "\"_calm_disturb_serial_\": [0");
            }
            do {
                if (value == digitalRead(TSKPIN)) {
                    if (g_sensor_debug && sumtimer > 0) {
                        len = strlen(buff);
                        if (len < MAX_BUF)
                            snprintf(buff + len, MAX_BUF - len - 1, ",%d", sumtimer);
                    }
                    sumtimer = 0;
                } else {
                    sumtimer += g_calm_step_ms;
                }
                delay(g_calm_step_ms);
            } while(g_current_sensor == s && sumtimer < g_calm_down_ms);
            g_repeat_counter += 1;
            _change_color_to(COLOR_BLACK);
            if (g_sensor_debug) {
                buff[strlen(buff)] = ']';
                _emq_report(buff);
            } else {
                _emq_report(NULL);
            }
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
    int i;
    while (1) {
        pthread_mutex_lock(&g_mutex);
        int s = g_current_sensor;
        pthread_mutex_unlock(&g_mutex);

        syslog(LOG_DEBUG, "change sensor [%d]\n", g_current_sensor);
        for (i = 0; i < 3; i++) {
            _change_color_to(g_current_color);
            delay(200);
            _change_color_to(COLOR_BLACK);
            delay(200);
        }

        switch (s) {
            case SENSOR_UNIVERSAL:
                _sensor_universal_task(s);
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
                while (g_current_sensor == s) {
                    _change_color_to(COLOR_MAGENTA);
                    delay(500);
                    _change_color_to(COLOR_BLACK);
                    delay(500);
                }
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

static int short_press_count = 0;
static time_t btn_onpress_timer = 0;

void sensor_detect()
{/*{{{*/
    if (BTN_RELEASE == digitalRead(BTNPIN)) {
        if (short_press_count > 0) {
            if ((time(0) - btn_onpress_timer) > 2) {
                syslog(LOG_DEBUG, "press count: %d\n", short_press_count);
                switch (short_press_count) {
                    case 2: {
                        syslog(LOG_DEBUG, "start ota auto upgrade!\n");
                        neza_pub("upgrade/auto", "{}");
                        break;
                    }
                    case 5: {
                        syslog(LOG_DEBUG, "start campi_frp.service!\n");
                        syscall_exec("systemctl start campi_frp.service");
                        break;
                    }
                    default: {
                        syslog(LOG_DEBUG, "no operation\n");
                    }
                }
                short_press_count = 0;
                _change_color_to(COLOR_BLACK);
            }
        }
        return;
    }

    static int duration = 0, color = COLOR_BLACK;
    time_t press_timer = time(0);
    while (BTN_ONPRESS == digitalRead(BTNPIN)) {
        duration = time(0) - press_timer;

        switch (duration) {
            case 0:
            case 1: color = COLOR_BLACK; break;
            case 2:
            case 3: color = COLOR_WHITE; break;
            case 4:
            case 5: color = COLOR_RED; break;
            case 6:
            case 7: color = COLOR_GREEN; break;
            case 8:
            case 9: color = COLOR_BLUE; break;
            case 10:
            case 11: color = COLOR_YELLOW; break;
            case 12:
            case 13: color = COLOR_CYAN; break;
            case 14:
            case 15: color = COLOR_MAGENTA; break;
            default: color = COLOR_BLACK;
        }
        _change_color_to(color);
        delay(20);
    }
    syslog(LOG_DEBUG, "duration: %d, color: %d\n", duration, color);

    if (color == COLOR_BLACK) { // short press
        short_press_count += 1;
        _change_color_to(short_press_count % 8);
        btn_onpress_timer = time(0);
    } else {
        short_press_count = 0;
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
                _change_sensor_to(color, SENSOR_NONE);
                break;
            }
        }
    }
    delay(200);
}/*}}}*/
