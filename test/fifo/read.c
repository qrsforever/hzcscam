#include <fcntl.h>
#include <stdio.h>
#include <sys/stat.h>
#include <unistd.h>
#include <time.h>

#define MAX_BUF 1024

int main()
{
    int fd;
    char * myfifo = "/tmp/myfifo";
    char buf[MAX_BUF] = { '0' };
    struct timespec ts = {0, 40000000}; // 40ms

    /* create the FIFO (named pipe) */
    int ret = access(myfifo, F_OK);
    if (0 != ret) {
        mkfifo(myfifo, 0666);
    }
    /* open the FIFO for reading */
    fd = open(myfifo, O_RDONLY | O_NONBLOCK);
    int num_bytes = read(fd, buf, MAX_BUF);
    for (; num_bytes > 0; ) {
        num_bytes = read(fd, buf, MAX_BUF);
    }
    
    while (1)
    {
        /* read from the FIFO */
        int num_bytes = read(fd, buf, MAX_BUF);
        if (num_bytes > 0)
        {
            buf[num_bytes] = 0;
            // printf("Received: %.*s\n", num_bytes, buf);
        }
        printf("%s\n", buf);
        nanosleep(&ts, NULL);
    }

    close(fd);
    return 0;
}
