#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

__led_blink yellow 3 0.5

source /campi/_env

for line in `${SYSROOT}/bin/logcat_start.sh 2>/dev/null`
do
    if [[ $line =~ logzip ]]
    then
        logpath=$(echo $line | cut -d: -f2)
        netok=$(ping -c 1 -W 2 www.baidu.com 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            python3 ${SYSROOT}/bin/send_log.py ${logpath}
            rm -rf ${logpath}
        else
            mv ${logpath} ${LOGS_PATH}/fail_reboot.tar.gz
        fi
    fi
done

__led_blink blue 6 0.5

# reboot -f
${SYSROOT}/bin/campi_safe_run.sh
