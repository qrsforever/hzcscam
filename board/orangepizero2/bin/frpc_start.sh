#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

TEST_DOMAIN="www.baidu.com"

while (( 1 ))
do
    if [[ x${TEST_DOMAIN} != x ]]
    then
        netok=$(ping -c 1 -W 2 ${TEST_DOMAIN} 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            __echo_and_run /usr/bin/frpc -c /etc/frp/frpc.ini
        fi
    fi
    sleep 10
done
