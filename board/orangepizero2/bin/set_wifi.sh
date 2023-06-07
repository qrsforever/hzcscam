#!/bin/bash

SSID=$1
PSWD=$2

WIRELESS_ADAPTER=${WIFI_DEVICE:-"wlan0"}

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

__echo_and_run nmcli device disconnect $WIRELESS_ADAPTER 2>/dev/null
__echo_and_run nmcli connection delete ${SSID} 2>/dev/null
__echo_and_run nmcli device wifi rescan; sleep 3

__echo_and_run nmcli device wifi connect "${SSID}" password "${PSWD}"

netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
if [[ x${netok} != x ]]
then
    # don't modify the "success" keys, check ok by `campi_cpi`
    echo "connect wifi [${SSID}] password [${PSWD}] success!"
else
    echo "connect wifi [${SSID}] password [${PSWD}] fail!"
fi
