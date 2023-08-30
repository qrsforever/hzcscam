#!/bin/bash

MNTDIR=${1:-/mnt/usb_sos}

ARCHIVES_ROOT_PATH=/var/campi/archives
RUNTIME_PATH=/campi/runtime

if [ ! -d ${MNTDIR} ]
then
    exit 1
fi

__led_blink() {
    color=$1
    count=${2:-3}
    interval=${3:-0.5}
    while (( count > 0 ))
    do
        sysled --color black
        sleep ${interval}
        sysled --color ${color}
        sleep ${interval}
        (( count -= 1 ))
    done
}

RUN_LOG=${MNTDIR}/campi/recovery.log

echo "start recovery ..." > ${RUN_LOG}

# set network
wififile=${MNTDIR}/campi/nmwifi.json
if [ -f ${wififile} ]
then
    wifissid=$(cat ${wififile} | jq -r ".wifissid")
    password=$(cat ${wififile} | jq -r ".password")
    echo "set wifi: ${wifissid} ${password}" >> ${RUN_LOG}
    nmcli device wifi rescan; sleep 3
    __led_blink red 3
    nmcli device wifi connect "${wifissid}" password "${password}"
    __led_blink red 3
fi

# set ota
otafile=${MNTDIR}/campi/version_info.json
if [ -f ${otafile} ]
then
    __led_blink green 2
    zipfil=$(cat ${otafile} | jq -r ".url")
    md5sum=$(cat ${otafile} | jq -r ".md5")
    compat=$(cat ${otafile} | jq -r ".compatible")
    rsetup=$(cat ${otafile} | jq -r ".execsetup")
    echo "upgrade: ${zipfil} ${md5sum} ${compat} ${rsetup}" >> ${RUN_LOG}
    rm -rf ${ARCHIVES_ROOT_PATH}/${md5sum}
    unzip -qo ${MNTDIR}/campi/${zipfil} -d ${ARCHIVES_ROOT_PATH}/${md5sum}
    if [ $? -ne 0 ]
    then
        echo "unzip ${MNTDIR}/campi/${zipfil} fail!!!" >> ${RUN_LOG}
    else
        __led_blink green 2
        if [ $compat == "true" ] && [ -f ${RUNTIME_PATH} ]
        then
            cp -aprf ${RUNTIME_PATH} ${ARCHIVES_ROOT_PATH}/${md5sum}
        fi
        if [ $rsetup == "true" ]
        then
            ${ARCHIVES_ROOT_PATH}/${md5sum}/scripts/setup_service.sh
        fi
        if [ -d  ${ARCHIVES_ROOT_PATH}/${md5sum} ]
        then
            rm -f /campi; ln -s ${ARCHIVES_ROOT_PATH}/${md5sum} /campi
        else
            echo "make soft link fail!!!" >> ${RUN_LOG}
        fi
        __led_blink green 2
    fi
fi

# set remote control
frpcfile=${MNTDIR}/campi/frpc
if [ -f ${frpcfile} ]
then
    __led_blink yellow 3
    echo "start frpc..." >> ${RUN_LOG}
    cp ${frpcfile} /tmp/
    chmod +x /tmp/frpc
    if [ -f "${frpcfile}.ini" ]
    then
        cp ${frpcfile}.ini /tmp/
    else
        ADDRESS=$(cat /sys/class/net/eth0/address | sed 's/://g')
        cat > /tmp/frpc.ini <<EOF
{
[common]
server_addr = 82.157.36.183
server_port = 7777

[ssh_${ADDRESS}_7722]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 7722
}
EOF
    fi
    /tmp/frpc -c /tmp/frpc.ini
fi

__led_blink white 5

echo "start main program" >> ${RUN_LOG}
systemctl start campi_boot.service
systemctl status campi_boot.service >> ${RUN_LOG}
