#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

TEST_DOMAIN="www.baidu.com"

if [ ! -e /etc/frp/frpc.ini ]
then
    mkdir -p /etc/frp/
    __echo_and_run cp /campi/extern/frp/arm64_c/frpc /usr/bin/frpc
    __echo_and_run cp /campi/extern/frp/arm64_c/frpc.ini /etc/frp/frpc.ini
fi

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
