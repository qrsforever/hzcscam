/******************************************************** **********************
* File:             main.c
*
* Author:
* Created:          06/01/23
* Description:
*****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <getopt.h>
#include <syslog.h>

#include "emqc.h"

extern int sensor_init();
extern void sensor_detect();

int main(int argc, char *argv[])
{
    char *emq_host = "tcp://aiot.hzcsdata.com";
    char *client_id = 0, *username = "campi", *password = "123456";
    int emq_port = 1883;

    int opt;
    int option_index = 0;
    const char *short_options = "c:u:p:";
    static struct option long_options[] = {
        {"emq_host" , required_argument , NULL , 'H'} ,
        {"emq_port" , required_argument , NULL , 'P'} ,
        {"client_id", required_argument , NULL , 'c'} ,
        {"username" , required_argument , NULL , 'u'} ,
        {"password" , required_argument , NULL , 'p'} ,
        {NULL       , 0                 , NULL , 0}   ,

    };

    openlog("campi_emq", LOG_CONS | LOG_PID, 0);
    while((opt = getopt_long(argc, argv, short_options, long_options, &option_index)) != -1) {
        switch (opt) {
            case 'H': {
                emq_host = optarg;
                break;
            }
            case 'P': {
                emq_port = atoi(optarg);
                break;
            }
            case 'c': {
                client_id = optarg;
                break;
            }
            case 'u': {
                username = optarg;
                break;
            }
            case 'p': {
                password = optarg;
                break;
            }
            default:
                break;
        }
    }
    printf("%s %d %s %s %s\n", emq_host, emq_port, client_id, username, password);
    emqc_connect(emq_host, emq_port, client_id, username, password);
    
    while (1) {
        emqc_yield();
    }
    closelog();
    return 0;
}
