#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

#define MAX_BUF 1024

int main()
{
    int fd;
    char * myfifo = "/tmp/myfifo";
    char buf[MAX_BUF];
    struct timespec ts = {0, 40000000}; // 40ms

    /* create the FIFO (named pipe) */
    int ret = access(myfifo, F_OK);
    if (0 != ret) {
        mkfifo(myfifo, 0666);
    }
    /* write "Hi" to the FIFO */
    fd = open(myfifo, O_RDWR | O_NONBLOCK);
    int size = fcntl(fd, F_SETPIPE_SZ, 16);
    size = fcntl(fd, F_GETPIPE_SZ);
    printf("size = %d\n", size);
    int i = 0;
    while (1)
    {
        snprintf(buf, MAX_BUF, "Hi:%d", i);
        int num_bytes = write(fd, buf, strlen(buf));
        if (num_bytes > 0)
        {
            printf("Send: %s\n", buf);
        }
        i++;
        sleep(1);
        // nanosleep(&ts, NULL);
    }

    close(fd);
    return 0;
}
