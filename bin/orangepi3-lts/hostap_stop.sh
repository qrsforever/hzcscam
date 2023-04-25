#!/bin/bash

echo "stop hostap..."

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

__echo_and_run systemctl daemon-reload
__echo_and_run nmcli con delete $(nmcli --fields NAME,UUID,TYPE con | grep wifi | awk '{print $2}') > /dev/null 2>&1
__echo_and_run rm -f /etc/network/interfaces.d/orangepi.ap.*
__echo_and_run rm -f /etc/dnsmasq.conf
__echo_and_run rm -f /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
__echo_and_run systemctl stop dnsmasq
# systemctl disable dnsmasq
__echo_and_run iptables -t nat -D POSTROUTING 1 >/dev/null 2>&1
__echo_and_run iptables -F
__echo_and_run systemctl stop orangepi-restore-iptables.service
__echo_and_run systemctl disable orangepi-restore-iptables.service
__echo_and_run rm -f /etc/iptables.ipv4.nat
__echo_and_run rm -f /var/run/hostapd/* >/dev/null 2>&1

__echo_and_run systemctl daemon-reload
__echo_and_run service NetworkManager stop >/dev/null 2>&1; sleep 1
__echo_and_run service dnsmasq stop; sleep 1; service hostapd stop; sleep 1
__echo_and_run service NetworkManager start >/dev/null 2>&1; sleep 1
__echo_and_run systemctl restart systemd-resolved.service

echo "stop hostap end..."
