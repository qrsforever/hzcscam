#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

source /campi/_env

__led_blink red 3 0.5

ARCHIVES_PATH=${ARCHIVES_PATH:-/var/campi/archives}
CURRENT_ARCHIVES_PATH=$(readlink /campi)

netok=$(ping -c 1 -W 2 www.baidu.com 2>/dev/null | grep -o "received")
if [[ x${netok} != x ]] && [[ -x ${SYSROOT}/bin/logcat_start.sh ]]
then
    for line in `${SYSROOT}/bin/logcat_start.sh 2>/dev/null`
    do
        if [[ $line =~ logzip ]]
        then
            logpath=$(echo $line | cut -d: -f2)
            python3 ${SYSROOT}/bin/send_log.py ${logpath}
            rm -rf ${logpath}
        fi
    done
    __led_blink magenta 3 0.5

fi

if [ $(basename ${CURRENT_ARCHIVES_PATH}) = factory ]
then
    echo "already factory mode!!!" > ${ARCHIVES_PATH}/campi_sos.log
    if [[ x${netok} != x ]]
    then
        systemctl start campi_frp.service
        count=100
        while (( count > 0 ))
        do
            sysled --color red; sleep 0.5; sysled --color green; sleep 0.5; sysled --color blue; sleep 0.5
            (( count -= 1 ))
        done
        systemctl stop campi_frp.service
    fi
    exit 1
fi

if [ ! -f ${ARCHIVES_PATH}/factory.zip ]
then
    echo "no factory.zip found!!!" > ${ARCHIVES_PATH}/campi_sos.log
    exit 1
fi
unzip -qo ${ARCHIVES_PATH}/factory.zip -d ${ARCHIVES_PATH}/factory_

if [ $? -ne 0 ]
then
    echo "unzip factory.zip fail!!!" > ${ARCHIVES_PATH}/campi_sos.log
    exit 1
fi

mv ${CURRENT_ARCHIVES_PATH}  /tmp/campi_sos

# for safe
rm -rf ${ARCHIVES_PATH}/factory
mv ${ARCHIVES_PATH}/factory_ ${ARCHIVES_PATH}/factory

if [[ -d /tmp/campi_sos/runtime ]]
then
    cp -arpf /tmp/campi_sos/runtime ${ARCHIVES_PATH}/factory/
fi

${ARCHIVES_PATH}/factory/scripts/setup_service.sh

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

__led_blink blue 6 0.5

# remove the problem update zip
rm -f ${ARCHIVES_PATH}/update.zip
rm -rf /tmp/campi_sos

# reboot -f
${SYSROOT}/bin/campi_safe_run.sh

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
