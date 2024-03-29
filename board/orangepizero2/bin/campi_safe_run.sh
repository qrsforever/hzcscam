#!/bin/bash

SAFE_RUN_LOG='/var/campi/campi_safe_run.log'
BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
BINDIR=/campi/board/${BOARD}/bin

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

count=3
while (( count > 0 ))
do
    sysled --color white
    sleep 0.5
    sysled --color magenta
    sleep 0.5
    (( count -= 1 ))
done

if [ -e ${SAFE_RUN_LOG} ]
then
    mv ${SAFE_RUN_LOG} ${SAFE_RUN_LOG}.pre
fi

echo "=======SAFE RUN========" > ${SAFE_RUN_LOG}

if [ -e /dev/sda1 ]
then
    MNTDIR=/mnt/usb_sos
    ARCHIVES_ROOT_PATH=/var/campi/archives
    RUNTIME_PATH=/campi/runtime
    mkdir -p ${MNTDIR}
    mount /dev/sda1 ${MNTDIR}

    # recovery scripts
    runscript=${MNTDIR}/campi/recovery.sh
    if [ -f $runscript ]
    then
        cp ${MNTDIR}/campi/recovery.sh /tmp/recovery.sh
        chmod +x /tmp/recovery.sh
        /tmp/recovery.sh ${MNTDIR} &
        exit 0
    fi

    # set network
    wififile=${MNTDIR}/campi/nmwifi.json
    if [ -f ${wififile} ]
    then
        wifissid=$(cat ${wififile} | jq -r ".wifissid")
        password=$(cat ${wififile} | jq -r ".password")
        echo "set wifi: ${wifissid} ${password}" >> ${SAFE_RUN_LOG}
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
        rsetup=$(cat ${otafile} | jq -r ".execsetup")
        rm -rf ${ARCHIVES_ROOT_PATH}/${md5sum}
        unzip -qo ${MNTDIR}/campi/${zipfil} -d ${ARCHIVES_ROOT_PATH}/${md5sum}
        if [ $? -ne 0 ]
        then
            echo "unzip ${MNTDIR}/campi/${zipfil} fail!!!" >> ${SAFE_RUN_LOG}
        else
            __led_blink green 2
            if [ $rsetup == "true" ]
            then
                NOCRON=1 ${ARCHIVES_ROOT_PATH}/${md5sum}/scripts/setup_service.sh
            fi
            if [ -d ${ARCHIVES_ROOT_PATH}/${md5sum} ]
            then
                rm -f /campi; ln -s ${ARCHIVES_ROOT_PATH}/${md5sum} /campi
                if [ -f ${wififile} ]
                then
                    cp ${wififile} /campi/runtime/
                fi
                sync
            else
                echo "make soft link fail!!!" >> ${SAFE_RUN_LOG}
            fi
            __led_blink green 2
        fi
    fi

    # set remote control
    frpcfile=${MNTDIR}/campi/frpc
    if [ -f ${frpcfile} ]
    then
        __led_blink yellow 3 2
        echo "start frpc..." >> ${SAFE_RUN_LOG}
        cp ${frpcfile} /tmp/
        chmod +x /tmp/frpc
        if [ -f "${frpcfile}.ini" ]
        then
            cp ${frpcfile}.ini /tmp/
        else
            ADDRESS=$(cat /sys/class/net/eth0/address | sed 's/://g')
            cat > /tmp/frpc.ini <<EOF
[common]
server_addr = 82.157.36.183
server_port = 7777

[ssh_${ADDRESS}_7722]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = 7722
EOF
        fi
        /tmp/frpc -c /tmp/frpc.ini
    fi
fi

echo "start main program" >> ${SAFE_RUN_LOG}
systemctl is-system-running >> ${SAFE_RUN_LOG}
systemctl list-unit-files | grep "campi" | tee -a ${SAFE_RUN_LOG}
systemctl restart campi_boot.service
