#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

source ${TOP_DIR}/_env

ARCHIVES_PATH=${ARCHIVES_PATH:-/var/campi/archives}

cp -arf ${ARCHIVES_PATH}/default ${ARCHIVES_PATH}/current

echo "${LD_LIBRARY_PATH}" > /tmp/campi_sos.log

rm /campi
ln -s ${ARCHIVES_PATH}/current /campi
for svc in ${CAMPI_ORDER_SVCS[@]}
do
    svc=campi_${svc}.service
    ret=$(systemctl is-active ${svc} | grep "active")
    if [[ x$ret == x ]]
    then
        echo "${svc} at $(date)" >> /tmp/campi_sos.log
        systemctl reset-failed  ${svc}
        systemctl restart ${svc}
    fi
done

exit 0
