#!/bin/bash

systemctl daemon-reload
nmcli con delete $(nmcli --fields NAME,UUID,TYPE con | grep wifi | awk '{print $2}')
sed 's/interface-name:wl.*//' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
sed 's/,$//' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
rm -f /etc/network/interfaces.d/orangepi.ap.*
rm -f /etc/dnsmasq.conf
systemctl stop dnsmasq
systemctl disable dnsmasq
iptables -t nat -D POSTROUTING 1 >/dev/null 2>&1
systemctl stop orangepi-restore-iptables.service
systemctl disable orangepi-restore-iptables.service
rm -f /etc/iptables.ipv4.nat
rm -f /var/run/hostapd/* >/dev/null 2>&1

systemctl daemon-reload
service NetworkManager stop >/dev/null 2>&1; sleep 1
service NetworkManager start >/dev/null 2>&1; sleep 1
systemctl restart systemd-resolved.service
