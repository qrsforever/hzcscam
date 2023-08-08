#!/bin/bash

SSID=$1
PSWD=$2

WIRELESS_ADAPTER=${WIFI_DEVICE:-"wlan0"}

__led_blink() {
    color=$1
    count=${2:-3}
    while (( count > 0 ))
    do
        sysled --color black
        sleep 1
        sysled --color ${color}
        (( count -= 1 ))
    done
}

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

__echo_and_run nmcli device disconnect $WIRELESS_ADAPTER 2>/dev/null
__echo_and_run nmcli connection delete ${SSID} 2>/dev/null
__echo_and_run nmcli device wifi rescan;

__led_blink yellow 3
__echo_and_run nmcli device wifi connect "${SSID}" password "${PSWD}"
__led_blink yellow 2

netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
if [[ x${netok} != x ]]
then
    # don't modify the "success" keys, check ok by `campi_cpi`
    echo "connect wifi [${SSID}] password [${PSWD}] success!"
else
    echo "connect wifi [${SSID}] password [${PSWD}] fail!"
fi
