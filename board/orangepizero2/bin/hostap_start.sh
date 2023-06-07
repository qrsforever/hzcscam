#!/bin/bash

## orangepi3-lts `source /etc/orangepi-release`

echo "start hostap..."

source /etc/orangepi-release
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $(dirname ${CUR_DIR}))
ETC_DIR=${TOP_DIR}/etc/${BOARD}

DEFAULT_ADAPTER="eth0"
WIRELESS_ADAPTER=${WIFI_DEVICE:-"wlan0"}

WIFI_SSID="CamPi-$(cat /sys/class/net/${DEFAULT_ADAPTER}/address | cut -d: -f5- | sed 's/://g')"
WIFI_PASS="88888888"
WIFI_WPSK=$(wpa_passphrase ${WIFI_SSID} ${WIFI_PASS} | grep '[^#]psk=' | grep psk | cut -d= -f2-)

echo "hostap ssid: ${WIFI_SSID} password: ${WIFI_PASS}"

__echo_and_run() {
    echo "$*"
    /bin/bash -c "$*"
}

systemctl daemon-reload

# remove interfaces from managed list
if [[ -f /etc/NetworkManager/conf.d/10-ignore-interfaces.conf ]]; then
    sed 's/interface-name:wl.*//' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
    sed 's/,$//' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
fi

# network settings
rm -f /etc/network/interfaces.d/orangepi.ap.nat
service networking restart
service NetworkManager restart >/dev/null 2>&1
sleep 3

# add interface to unmanaged list
echo "[keyfile]" > /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
echo "unmanaged-devices=interface-name:$WIRELESS_ADAPTER" >> /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
service NetworkManager reload >/dev/null 2>&1

# set hostapd.conf
__echo_and_run cp ${ETC_DIR}/hostapd.conf /etc/hostapd.conf
__echo_and_run cp ${ETC_DIR}/dnsmasq.conf /etc/dnsmasq.conf
__echo_and_run cp ${ETC_DIR}/orangepi.ap.nat /etc/network/interfaces.d/orangepi.ap.nat
sed -i "s/^ssid=.*/ssid=${WIFI_SSID}/" /etc/hostapd.conf
sed -i "s/^wpa_passphrase=.*/wpa_passphrase=${WIFI_PASS}/" /etc/hostapd.conf
sed -i "s/^wpa_psk=.*/wpa_psk=${WIFI_WPSK}/" /etc/hostapd.conf
sed -i "s/^interface=.*/interface=$WIRELESS_ADAPTER/" /etc/hostapd.conf
sed -i "s/^interface=.*/interface=$WIRELESS_ADAPTER/" /etc/dnsmasq.conf
sed -i "s/plug\ .*/plug\ $WIRELESS_ADAPTER/" /etc/network/interfaces.d/orangepi.ap.nat
sed -i "s/iface .* inet*/iface $WIRELESS_ADAPTER inet/" /etc/network/interfaces.d/orangepi.ap.nat
sed -i "s/^DAEMON_CONF=.*/DAEMON_CONF=\/etc\/hostapd.conf/" /etc/init.d/hostapd

# iptables
#
sed -i "/net.ipv4.ip_forward=/c\net.ipv4.ip_forward=1" /etc/sysctl.conf
echo 1 > /proc/sys/net/ipv4/ip_forward
__echo_and_run iptables-save | awk '/^[*]/ { print $1 } /^:[A-Z]+ [^-]/ { print $1 " ACCEPT" ; } /COMMIT/ { print $0; }' | iptables-restore
__echo_and_run iptables -t nat -A POSTROUTING -o $DEFAULT_ADAPTER -j MASQUERADE
__echo_and_run iptables -A FORWARD -i $DEFAULT_ADAPTER -o $WIRELESS_ADAPTER -m state --state RELATED,ESTABLISHED -j ACCEPT
__echo_and_run iptables -A FORWARD -i $WIRELESS_ADAPTER -o $DEFAULT_ADAPTER -j ACCEPT
__echo_and_run iptables-save > /etc/iptables.ipv4.nat

# systemctl stop orangepi-restore-iptables.service
# systemctl disable orangepi-restore-iptables.service
# cat <<-EOF > /etc/systemd/system/orangepi-restore-iptables.service
# [Unit]
# Description="Restore IP tables"
# [Timer]
# OnBootSec=20Sec
# [Service]
# Type=oneshot
# ExecStart=/sbin/iptables-restore /etc/iptables.ipv4.nat
# [Install]
# WantedBy=sysinit.target
# EOF
# systemctl enable orangepi-restore-iptables.service

__echo_and_run ifdown $WIRELESS_ADAPTER 2> /dev/null
sleep 1
__echo_and_run ifup $WIRELESS_ADAPTER 2> /dev/null

# reload services
__echo_and_run systemctl daemon-reload
# __echo_and_run systemctl enable dnsmasq; sleep 1
__echo_and_run service NetworkManager stop >/dev/null 2>&1; sleep 1
__echo_and_run service dnsmasq stop; sleep 1
__echo_and_run service hostapd stop; sleep 1
__echo_and_run service dnsmasq start; sleep 2
__echo_and_run service hostapd start; sleep 2
__echo_and_run service NetworkManager start >/dev/null 2>&1; sleep 2
__echo_and_run systemctl restart systemd-resolved.service

echo "start hostap end..."
