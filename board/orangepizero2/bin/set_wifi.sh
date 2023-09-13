#!/bin/bash

SSID=$1
PSWD=$2
BSSID=$3

WIRELESS_ADAPTER=${WIFI_DEVICE:-"wlan0"}

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

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

__led_blink green 3 1

__echo_and_run nmcli device disconnect $WIRELESS_ADAPTER 2>/dev/null
for uuid in $(nmcli --terse --fields UUID connection show)
do 
    __echo_and_run nmcli connection delete ${uuid} 2>/dev/null
done
__echo_and_run nmcli device wifi rescan;

__led_blink green 5 0.5

if [[ x${BSSID} != x ]] && [[ x$(nmcli -f bssid device wifi list | grep ${BSSID}) != x ]]
then
    __echo_and_run nmcli device wifi connect "${SSID}" password "${PSWD}" bssid ${BSSID}
else
    __echo_and_run nmcli device wifi connect "${SSID}" password "${PSWD}"
fi
__led_blink green 7 0.2

netok=$(nmcli --fields STATE,DEVICE device status | grep "^connected" | grep "$WIRELESS_ADAPTER")
if [[ x${netok} != x ]]
then
    # don't modify the "success" keys, check ok by `campi_cpi`
    echo "connect wifi [${SSID}] password [${PSWD}] success!"
else
    echo "connect wifi [${SSID}] password [${PSWD}] fail!"
fi
