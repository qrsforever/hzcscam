#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)
DST_DIR=/etc/systemd/system/

SERVICE=hotspot.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)

cat > $TOP_DIR/etc/systemd/$SERVICE <<EOF
[Unit]
    Description=AP
    Documentation=http://campi.hzcsai.com
    StartLimitIntervalSec=120
    StartLimitBurst=5
    OnFailure=jetsos.service

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$ROOT_DIR
    Restart=always
    RestartSec=3
    ExecStart=$ROOT_DIR/bin/${BOARD}/hostap_start.sh
    ExecStopPost=-$ROOT_DIR/bin/${BOARD}/hostap_stop.sh
    KillSignal=SIGINT
    TimeoutStartSec=20
    TimeoutStopSec=30
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE
cp $TOP_DIR/etc/systemd/$SERVICE $DST_DIR
systemctl daemon-reload
systemctl enable $SERVICE
systemctl restart $SERVICE
systemctl status $SERVICE
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
