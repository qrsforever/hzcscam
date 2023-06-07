#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

source ${TOP_DIR}/_env

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    echo "${svc} at $(date)" >> /tmp/campi_reboot.log
    svc=campi_${svc}.service
    systemctl start ${svc}
done
