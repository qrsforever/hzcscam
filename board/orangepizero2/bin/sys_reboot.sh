#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=/campi

source ${TOP_DIR}/_env

__run_and_log() {
    echo "$*"
    /bin/bash -c "$*" >> /tmp/campi_reboot.log
}

if [[ ! -e ${TOP_DIR}/runtime/nmwifi.json ]]
then
    mkdir -p ${TOP_DIR}/runtime
    cp ${SYSROOT}/etc/nmwifi.json ${TOP_DIR}/runtime/nmwifi.json
fi

echo "==============Network=================" > /tmp/campi_reboot.log
__run_and_log nmcli device status
echo "==============Memory=================" >> /tmp/campi_reboot.log
__run_and_log free
echo "===============Disk==================" >> /tmp/campi_reboot.log
__run_and_log df
echo "==============Campi==================" >> /tmp/campi_reboot.log
__run_and_log ls -l ${TOP_DIR}/runtime


netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
if [[ x${netok} == x && -f ${TOP_DIR}/runtime/nmwifi.json ]]
then
    wifissid=$(cat ${TOP_DIR}/runtime/nmwifi.json | jq -r ".wifissid")
    password=$(cat ${TOP_DIR}/runtime/nmwifi.json | jq -r ".password")
    __run_and_log nmcli device wifi rescan; sleep 5
    __run_and_log ${SYSROOT}/bin/set_wifi.sh ${wifissid} ${password}
fi

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    echo "start ${svc} at $(date)" >> /tmp/campi_reboot.log
    svc=campi_${svc}.service
    systemctl start ${svc}
done