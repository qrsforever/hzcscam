#!/bin/bash

if [ -e /dev/sda1 ]
then
    mkdir -p /mnt/usb_sos
    mount /dev/sda1 /mnt/usb_sos
    wififile=/mnt/usb_sos/campi/nmwifi.json
    if [ -f ${wififile} ]
    then
        wifissid=$(cat ${wififile} | jq -r ".wifissid")
        password=$(cat ${wififile} | jq -r ".password")
        nmcli device wifi rescan; sleep 3
        nmcli device wifi connect ${wifissid} password "${password}"
    fi

    frpcfile=/mnt/usb_sos/campi/frpc
    if [ -f ${frpcfile} ]
    then
        cp "${frpcfile}*" /tmp/
        chmod +x /tmp/frpc
        /bin/frpc -c /tmp/frpc.json
    fi
else
    echo "not found /dev/sda1" > /var/sos.txt
fi
