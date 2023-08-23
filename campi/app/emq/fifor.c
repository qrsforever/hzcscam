/******************************************************************************
* File:             fifor.c
*
* Author:           erlangai
* Created:          06/27/23
* Description:
*****************************************************************************/

#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>
#include <string.h>

#define MAX_BUF 1024
#define PIEMQ_FIFO   "/tmp/emq_sensor.fifo"

int main()
{
    int fd;
    int num_bytes, pre_bytes = 2;
    char buff[MAX_BUF] = { 0 };
    struct timespec ts = {0, 70000000}; // 70ms

    if (0 != access(PIEMQ_FIFO, F_OK))
        mkfifo(PIEMQ_FIFO, 0666);

    fd = open(PIEMQ_FIFO, O_RDONLY | O_NONBLOCK);
    num_bytes = read(fd, buff, MAX_BUF);
    for (; num_bytes > 0; )
        num_bytes = read(fd, buff, MAX_BUF);
    buff[0] = '0';
    buff[1] = '\n';
    buff[2] = 0;
    while (1) {
        num_bytes = read(fd, buff, MAX_BUF);
        if (num_bytes > 0) {
            buff[num_bytes] = '\n';
            pre_bytes = num_bytes + 1;
        }
        if (pre_bytes != write(STDOUT_FILENO, buff, pre_bytes))
            break;
        nanosleep(&ts, NULL);
    }
    close(fd);
    return 0;
}
