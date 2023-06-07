#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$1

source ${TOP_DIR}/_env

__run_and_log() {
    echo "$*"
    /bin/bash -c "$*" >> /tmp/campi_reboot.log
}

echo "==============Network================="
__run_and_log nmcli device status
echo "==============Memory================="
__run_and_log free
echo "==============Disk================="
__run_and_log df

netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
if [[ x${netok} != x && -f ${TOP_DIR}/runtime/nmwifi.json ]]
then
    if 
    ${CUR_DIR}/set_wifi.sh
fi

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    echo "start ${svc} at $(date)" >> /tmp/campi_reboot.log
    svc=campi_${svc}.service
    systemctl start ${svc}
done
