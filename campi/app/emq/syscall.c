/******************************************************************************
* File:             syscall.c
*
* Author:           erlangai  
* Created:          06/21/23 
* Description:      
*****************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#define MAX_CMD_LENGTH 128

static int g_write_fd = -1;

extern int syscall_init();
extern int syscall_exec(const char* cmd);

int syscall_init()
{
    int fd[2];
    int ret = -1;
    ret = pipe(fd);
    if (fork() == 0) {
        // child process
        close(fd[1]);
        char cmd[MAX_CMD_LENGTH];
        while (read(fd[0], cmd, MAX_CMD_LENGTH) > 0) {
            ret = system(cmd);
            printf("system call: %s [%d]", cmd, ret);
        }
    }
    // parent process
    close(fd[0]);
    g_write_fd = fd[1];
    return 0;
}

int syscall_exec(const char *cmd)
{
    if (g_write_fd < 0)
        return -1;
    return write(g_write_fd, cmd, strlen(cmd) + 1);
}
