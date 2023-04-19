#!/bin/bash

## orangepi3-lts `source /etc/orangepi-release`

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $(dirname ${CUR_DIR}))
ETC_DIR=${TOP_DIR}/etc/orangepi3-lts

WIRELESS_ADAPTER=${WIFI_DEVICE: -'wlan0'}

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

service NetworkManager reload >/dev/null 2>&1
# add interface to unmanaged list
if [[ -f /etc/NetworkManager/conf.d/10-ignore-interfaces.conf ]]; then
    [[ -z $(grep -w unmanaged-devices= /etc/NetworkManager/conf.d/10-ignore-interfaces.conf) ]] && sed '$ s/$/,/' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
    sed '$ s/$/'"interface-name:$WIRELESS_ADAPTER"'/' -i /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
else
    echo "[keyfile]" > /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
    echo "unmanaged-devices=interface-name:$WIRELESS_ADAPTER" >> /etc/NetworkManager/conf.d/10-ignore-interfaces.conf
fi
service NetworkManager reload >/dev/null 2>&1

# set hostapd.conf
cp ${ETC_DIR}/hostapd.conf /etc/hostapd.conf
cp ${ETC_DIR}/dnsmasq.conf /etc/dnsmasq.conf
cp ${ETC_DIR}/orangepi.ap.nat /etc/network/interfaces.d/orangepi.ap.nat
sed -i "s/^interface=.*/interface=$WIRELESS_ADAPTER/" /etc/hostapd.conf
sed -i "s/^interface=.*/interface=$WIRELESS_ADAPTER/" /etc/dnsmasq.conf
sed -i "s/plug\ .*/plug\ $WIRELESS_ADAPTER/" /etc/orangepi3-lts/orangepi.ap.nat 
sed -i "s/iface .* inet*/iface $WIRELESS_ADAPTER inet/" /etc/orangepi3-lts/orangepi.ap.nat 
# add hostapd.conf to services
sed -i "s/^DAEMON_CONF=.*/DAEMON_CONF=\/etc\/hostapd.conf/" /etc/init.d/hostapd

# iptables
sed -i "/net.ipv4.ip_forward=/c\net.ipv4.ip_forward=1" /etc/sysctl.conf
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables-save | awk '/^[*]/ { print $1 } /^:[A-Z]+ [^-]/ { print $1 " ACCEPT" ; } /COMMIT/ { print $0; }' | iptables-restore
iptables -t nat -A POSTROUTING -o $DEFAULT_ADAPTER -j MASQUERADE
iptables -A FORWARD -i $DEFAULT_ADAPTER -o $WIRELESS_ADAPTER -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $WIRELESS_ADAPTER -o $DEFAULT_ADAPTER -j ACCEPT
iptables-save > /etc/iptables.ipv4.nat
systemctl stop orangepi-restore-iptables.service
systemctl disable orangepi-restore-iptables.service
cat <<-EOF > /etc/systemd/system/orangepi-restore-iptables.service
[Unit]
Description="Restore IP tables"
[Timer]
OnBootSec=20Sec
[Service]
Type=oneshot
ExecStart=/sbin/iptables-restore /etc/iptables.ipv4.nat
[Install]
WantedBy=sysinit.target
EOF
systemctl enable orangepi-restore-iptables.service

ifdown $WIRELESS_ADAPTER 2> /dev/null
sleep 2
ifup $WIRELESS_ADAPTER 2> /dev/null

# reload services
systemctl daemon-reload
systemctl enable dnsmasq; sleep 1
service NetworkManager stop >/dev/null 2>&1; sleep 1
service dnsmasq start; sleep 1
service hostapd start; sleep 1
service NetworkManager start >/dev/null 2>&1; sleep 1
systemctl restart systemd-resolved.service
