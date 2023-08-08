/******************************************************************************
* File:             sysled.c
*
* Author:
* Created:          08/08/23
* Description:
*****************************************************************************/

#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <getopt.h>
#include <wiringPi.h>

#define REDLED   5    // PC6
#define GREENLED 7    // PC5
#define BLUELED  8    // PC8

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


static void _change_color_to(int c)/*{{{*/
{
    digitalWrite(REDLED   , _RGB[c][0]);
    digitalWrite(GREENLED , _RGB[c][1]);
    digitalWrite(BLUELED  , _RGB[c][2]);
}/*}}}*/

int sysled_init()
{/*{{{*/
    if(wiringPiSetup() == -1) {
        exit(1);
    }

    pinMode(REDLED, OUTPUT);
    pinMode(BLUELED, OUTPUT);
    pinMode(GREENLED, OUTPUT);
    return 0;
}/*}}}*/


int main(int argc, char *argv[])
{
    int color = COLOR_BLACK;
    int opt;
    int option_index = 0;
    const char *short_options = "c:";
    static struct option long_options[] = {
        {"color", required_argument, NULL, 'c'} ,
        {NULL, 0, NULL, 0},
    };

    while((opt = getopt_long(argc, argv, short_options, long_options, &option_index)) != -1) {
        switch (opt) {
            case 'c': {
                if (0 == strcmp("red", optarg)) {
                    color = COLOR_RED;
                } else if (0 == strcmp("green", optarg)) {
                    color = COLOR_GREEN;
                } else if (0 == strcmp("blue", optarg)) {
                    color = COLOR_BLUE;
                } else if (0 == strcmp("yellow", optarg)) {
                    color = COLOR_YELLOW;
                } else if (0 == strcmp("cyan", optarg)) {
                    color = COLOR_CYAN;
                } else if (0 == strcmp("magenta", optarg)) {
                    color = COLOR_MAGENTA;
                } else if (0 == strcmp("white", optarg)) {
                    color = COLOR_WHITE;
                }
                break;
            }
            default:
                break;
        }
    }
    sysled_init();
    _change_color_to(color);
    return 0;
}
