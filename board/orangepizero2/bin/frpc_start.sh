#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source /campi/_env

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

TEST_DOMAIN="www.baidu.com"
FRPC_INI="${RUNTIME_PATH}/frpc.ini"

if [[ ! -e ${FRPC_INI} ]]
then
    FRPC_INI="/tmp/frpc.ini"
    cp ${SYSROOT}/etc/frpc.ini ${FRPC_INI}
    sed -i "s/ssh/ssh_${ADDRESS}/g" ${FRPC_INI}
else
    touch ${RUNTIME_PATH}/start/frp
fi

while (( 1 ))
do
    if [[ x${TEST_DOMAIN} != x ]]
    then
        netok=$(ping -c 1 -W 2 ${TEST_DOMAIN} 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            __echo_and_run ${SYSROOT}/bin/frpc -c ${FRPC_INI}
        fi
    fi
    sleep 20
done
