#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

source /campi/_env

ARCHIVES_PATH=${ARCHIVES_PATH:-/var/campi/archives}

CURRENT_ARCHIVES_PATH=$(readlink /campi)

mv ${CURRENT_ARCHIVES_PATH}  /tmp/campi_sos
unzip -qo ${ARCHIVES_PATH}/factory.zip -d ${ARCHIVES_PATH}/factory

if [[ -d /tmp/campi_sos/runtime ]]
then
    cp -arpf /tmp/campi_sos/runtime ${ARCHIVES_PATH}/factory/
fi

rm -f /campi
ln -s ${ARCHIVES_PATH}/factory /campi

logsize=`stat --format=%s ${ARCHIVES_PATH}/campi_sos.log`
if (( ${logsize} > 10240 ))
then
    rm ${ARCHIVES_PATH}/campi_sos.log
fi

from=$(cat /tmp/campi_sos/version.txt)
to=$(cat /campi/version.txt)

echo "$(date +"%Y/%m/%d-%H:%M:%S") from ${from} to ${to}"  >> ${ARCHIVES_PATH}/campi_sos.log

reboot

# for svc in ${CAMPI_ORDER_SVCS[@]}
# do
#     svc=campi_${svc}.service
#     ret=$(systemctl is-active ${svc} | grep "active")
#     if [[ x$ret == x ]]
#     then
#         echo "${svc} at $(date)" >> /tmp/campi_sos.log
#         systemctl reset-failed  ${svc}
#         systemctl restart ${svc}
#     fi
# done
# exit 0
