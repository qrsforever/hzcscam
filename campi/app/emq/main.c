/******************************************************** **********************
* File:             main.c
*
* Author:
* Created:          06/01/23
* Description:
*****************************************************************************/

#include<stdio.h>
#include<unistd.h>
#include<getopt.h>


int main(int argc, char *argv[])
{
    int opt;
    int option_index = 0;
    const char *short_options = "c:u:p";
    x

    static struct option long_options[] = {
        {"emqx_host" , required_argument , NULL , 'H'} , 
        {"emqx_port" , optional_argument , NULL , 'P'} , 
        {"client_id" , required_argument , NULL , 'c'} , 
        {"username"  , required_argument , NULL , 'u'} , 
        {"password"  , required_argument , NULL , 'p'} , 
        {NULL        , 0                 , NULL , 0}   , 

    };

    while((opt = getopt_long(argc, argv, short_options, long_options, &option_index)) != -1) {


    }
}
