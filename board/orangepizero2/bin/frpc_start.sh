#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source /campi/_env

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

TEST_DOMAIN="www.baidu.com"

if [[ ! -e /campi/runtime/frpc.ini ]]
then
    cp ${SYSROOT}/etc/frpc.ini /campi/runtime/frpc.ini
fi

while (( 1 ))
do
    if [[ x${TEST_DOMAIN} != x ]]
    then
        netok=$(ping -c 1 -W 2 ${TEST_DOMAIN} 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            __echo_and_run ${SYSROOT}/bin/frpc -c /campi/runtime/frpc.ini
        fi
    fi
    sleep 20
done
