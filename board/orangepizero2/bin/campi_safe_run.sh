#!/bin/bash

SAFE_RUN_LOG='/var/campi_safe_run.log'

echo "=======SAFE RUN========" > ${SAFE_RUN_LOG}

if [ -e /dev/sda1 ]
then
    MNTDIR=/mnt/usb_sos
    ARCHIVES_ROOT_PATH=/var/campi/archives
    RUNTIME_PATH=/campi/runtime
    mkdir -p ${MNTDIR}
    mount /dev/sda1 ${MNTDIR}

    # set network
    wififile=${MNTDIR}/campi/nmwifi.json
    if [ -f ${wififile} ]
    then
        wifissid=$(cat ${wififile} | jq -r ".wifissid")
        password=$(cat ${wififile} | jq -r ".password")
        echo "set wifi: ${wifissid} ${password}" >> ${SAFE_RUN_LOG}
        nmcli device wifi rescan; sleep 3
        nmcli device wifi connect "${wifissid}" password "${password}"
        sleep 3
    fi

    # set ota
    otafile=${MNTDIR}/campi/version_info.json
    if [ -f ${otafile} ]
    then
        zipfil=$(cat ${otafile} | jq -r ".url")
        md5sum=$(cat ${otafile} | jq -r ".md5")
        compat=$(cat ${otafile} | jq -r ".compatible")
        rsetup=$(cat ${otafile} | jq -r ".execsetup")

        unzip -qo ${MNTDIR}/campi/${zipfil} -d ${ARCHIVES_ROOT_PATH}/${md5sum}
        if [ $compat == "true" ] && [ -f ${RUNTIME_PATH} ]
        then
            cp -aprf ${RUNTIME_PATH} ${ARCHIVES_ROOT_PATH}/${md5sum}
        fi
        if [ $rsetup == "true" ]
        then
            ${ARCHIVES_ROOT_PATH}/${md5sum}/scripts/setup_service.sh
        fi
        rm -f /campi; ln -s ${ARCHIVES_ROOT_PATH}/${md5sum} /campi
    fi

    # set remote control
    frpcfile=${MNTDIR}/campi/frpc
    if [ -f ${frpcfile} ]
    then
        echo "start frpc..." >> ${SAFE_RUN_LOG}
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

    [${ADDRESS}_7722]
    type = tcp
    local_ip = 127.0.0.1
    local_port = 22
    remote_port = 7722
}
EOF
        fi
        /tmp/frpc -c /tmp/frpc.ini
    fi
fi

echo "start main program" >> ${SAFE_RUN_LOG}
BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
BINDIR=/campi/board/${BOARD}/bin
${BINDIR}/sys_reboot.sh
