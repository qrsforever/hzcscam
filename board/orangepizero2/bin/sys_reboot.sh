#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=/campi

source ${TOP_DIR}/_env
rm -rf ${TOP_DIR}/*-1883

RUNTIME_PATH=${RUNTIME_PATH:-/campi/runtime}
LOGS_PATH=${LOGS_PATH:-/campi/logs}

echo "===============SYS REBOOT==============" > ${LOGS_PATH}/campi_reboot.log

__led_blink red 3

if [ ! -d ${RUNTIME_PATH}/start ]
then
    mkdir -p ${RUNTIME_PATH}/start
fi

if [ ! -d ${RUNTIME_PATH} ]
then
    mkdir -p ${LOGS_PATH}
fi

if [[ ! -e ${RUNTIME_PATH}/gst_rtmp.env ]]
then
    cp ${SYSROOT}/etc/gst_rtmp.env ${RUNTIME_PATH}/gst_rtmp.env
fi

__run_and_log() {
    echo "$*"
    /bin/bash -c "$*" >> ${LOGS_PATH}/campi_reboot.log
}

if [[ ! -e ${TOP_DIR}/runtime/nmwifi.json ]]
then
    mkdir -p ${TOP_DIR}/runtime
    cp ${SYSROOT}/etc/nmwifi.json ${TOP_DIR}/runtime/nmwifi.json
fi

echo "==============Network================" >> ${LOGS_PATH}/campi_reboot.log
__run_and_log nmcli device status
echo "==============Memory=================" >> ${LOGS_PATH}/campi_reboot.log
__run_and_log free
echo "===============Disk==================" >> ${LOGS_PATH}/campi_reboot.log
__run_and_log df
echo "==============Campi==================" >> ${LOGS_PATH}/campi_reboot.log
__run_and_log ls -l ${TOP_DIR}/runtime

# TODO set_wifi will delete wifi connection
# netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
# if [[ x${netok} == x && -f ${TOP_DIR}/runtime/nmwifi.json ]]
# then
    wifissid=$(cat ${TOP_DIR}/runtime/nmwifi.json | jq -r ".wifissid")
    password=$(cat ${TOP_DIR}/runtime/nmwifi.json | jq -r ".password")
    if [[ -z $(nmcli --fields NAME connection | grep ${wifissid}) ]]
    then
        __run_and_log ${SYSROOT}/bin/set_wifi.sh ${wifissid} ${password}
    else
        __run_and_log nmcli device wifi rescan
        __led_blink green 2 0.3
        __run_and_log nmcli connection down ${wifissid}
        __led_blink green 2 0.3
        __run_and_log nmcli connection up ${wifissid}
        __led_blink green 2 0.3
        __run_and_log nmcli device wifi connect ${wifissid} password "${password}"
        __led_blink green 2 0.3
    fi
    i=0
    while (( i < 5 ))
    do
        netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
        if [[ -z ${netok} ]]
        then
            __led_blink blue 2 0.5
            (( i += 1 ))
            continue
        fi
        break
    done
    if (( i == 5 ))
    then
        __led_blink red 2
        __led_blink green 2
        __led_blink blue 2
        reboot
    fi
# fi

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    echo "start ${svc} at $(date +"%Y/%m/%d-%H:%M:%S")" >> ${LOGS_PATH}/campi_reboot.log
    svc=campi_${svc}.service
    systemctl start ${svc}
    __led_blink yellow 2 0.2
done

for svc in `ls ${RUNTIME_PATH}/start`
do
    echo "start ${svc} at $(date +"%Y/%m/%d-%H:%M:%S")" >> ${LOGS_PATH}/campi_reboot.log
    svc=campi_${svc}.service
    systemctl start ${svc}
    __led_blink cyan 2 0.2
done
