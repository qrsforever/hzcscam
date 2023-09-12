#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=/campi

source ${TOP_DIR}/_env
rm -rf ${TOP_DIR}/*-1883

RUNTIME_PATH=${RUNTIME_PATH:-/campi/runtime}
LOGS_PATH=${LOGS_PATH:-/campi/logs}

if [ -e ${LOGS_PATH}/campi_reboot.log ]
then
    mv ${LOGS_PATH}/campi_reboot.log ${LOGS_PATH}/campi_reboot.log.pre
fi

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
    expbssid=$(cat ${TOP_DIR}/runtime/nmwifi.json | jq -r ".expbssid" | grep -v "null")
    echo "${wifissid}:[${password}]" >> ${LOGS_PATH}/campi_reboot.log
    if [[ -z $(nmcli --fields NAME connection | grep ${wifissid}) ]]
    then
        __run_and_log ${SYSROOT}/bin/set_wifi.sh ${wifissid} ${password} ${expbssid}
    else
        __run_and_log nmcli device wifi rescan
        __led_blink green 2 0.5
        __run_and_log nmcli connection down ${wifissid}
        __led_blink green 2 0.5
        __run_and_log nmcli connection up ${wifissid}
        __led_blink green 2 0.5
        if [[ x$expbssid != x ]]
        then
            __run_and_log nmcli device wifi connect ${wifissid} password "${password}" bssid=${expbssid}
        else
            __run_and_log nmcli device wifi connect ${wifissid} password "${password}"
        fi
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
        # TODO some orangepizero2 cannot boot
        # reboot -f
        nmcli --fields STATE,DEVICE device status  >> ${LOGS_PATH}/campi_reboot.log
        echo "${wifissid}:[${password}] try connect fail!" >> ${LOGS_PATH}/campi_reboot.log
        nohup ${SYSROOT}/bin/campi_safe_run.sh &
        exit 0
    fi
# fi

if [[ -f ${LOGS_PATH}/fail_reboot.tar.gz ]]
then
    python3 ${SYSROOT}/bin/send_log.py ${LOGS_PATH}/fail_reboot.tar.gz
    rm -f ${LOGS_PATH}/fail_reboot.tar.gz
fi

__led_blink white 2 0.3

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    svc=campi_${svc}.service
    systemctl stop ${svc}
done

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    echo "start ${svc} at $(date +"%Y/%m/%d-%H:%M:%S")" >> ${LOGS_PATH}/campi_reboot.log
    svc=campi_${svc}.service
    __led_blink magenta 1 0.3
    systemctl start ${svc}
done

for svc in `ls ${RUNTIME_PATH}/start`
do
    echo "start ${svc} at $(date +"%Y/%m/%d-%H:%M:%S")" >> ${LOGS_PATH}/campi_reboot.log
    svc=campi_${svc}.service
    systemctl restart ${svc}
done
