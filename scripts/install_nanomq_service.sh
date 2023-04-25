#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(dirname $CUR_DIR)

SERVICE=campi_nanomq.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
SRC_DIR=${TOP_DIR}/etc/${BOARD}
DST_DIR=/etc/systemd/system/

cat > ${SRC_DIR}/$SERVICE <<EOF
[Unit]
    Description=NanoMQ
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
    ExecStart=${TOP_DIR}/bin/${BOARD}/nanomq start
    ExecStop=${TOP_DIR}/bin/${BOARD}/nanomq stop
    TimeoutStartSec=3
    TimeoutStopSec=3
    StandardOutput=syslog
    StandardError=syslog

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE 2>&1 /dev/null
cp ${SRC_DIR}/$SERVICE $DST_DIR
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
