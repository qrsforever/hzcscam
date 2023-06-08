#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source /campi/_env

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

if [[ ! -e /campi/runtime/emqx.env ]]
then
    cp ${SYSROOT}/etc/emqx.env /campi/runtime/emqx.env
fi

source /campi/runtime/emqx.env

while (( 1 ))
do
    if [[ x${EMQ_HOST} != x ]]
    then
        netok=$(ping -c 1 -W 2 ${EMQ_HOST} 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            ${SYSROOT}/bin/emqs \
                --emq_host ${EMQ_HOST} \
                --emq_port ${EMQ_PORT:-1883} \
                -c ${EMQ_CLIENTID} -u ${EMQ_USERNAME} -p ${EMQ_PASSWORD}
        fi
    fi
    sleep 10
done