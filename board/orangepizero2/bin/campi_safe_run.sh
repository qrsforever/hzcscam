#!/bin/bash

SAFE_RUN_LOG='/var/campi_safe_run.log'

echo "=======SAFE RUN========" > ${SAFE_RUN_LOG}

if [ -e /dev/sda1 ]
then
    mkdir -p /mnt/usb_sos
    mount /dev/sda1 /mnt/usb_sos
    wififile=/mnt/usb_sos/campi/nmwifi.json
    if [ -f ${wififile} ]
    then
        wifissid=$(cat ${wififile} | jq -r ".wifissid")
        password=$(cat ${wififile} | jq -r ".password")
        echo "set wifi: ${wifissid} ${password}" >> ${SAFE_RUN_LOG}
        nmcli device wifi rescan; sleep 3
        nmcli device wifi connect "${wifissid}" password "${password}"
    fi

    sleep 3

    frpcfile=/mnt/usb_sos/campi/frpc
    if [ -f ${frpcfile} ]
    then
        echo "start frpc..." >> ${SAFE_RUN_LOG}
        cp "${frpcfile}*" /tmp/
        chmod +x /tmp/frpc
        /tmp/frpc -c /tmp/frpc.json
    fi

    sleep 3
fi

echo "start main program" >> ${SAFE_RUN_LOG}
BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
BINDIR=/campi/board/${BOARD}/bin
${BINDIR}/sys_reboot.sh
