#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

SERVICE=campi_nmq.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
SRC_DIR=${ROOT_DIR}/runtime
DST_DIR=/etc/systemd/system/

cat > ${SRC_DIR}/$SERVICE <<EOF
[Unit]
    Description=NanoMQ
    Documentation=http://campi.hzcsai.com
    StartLimitIntervalSec=120
    StartLimitBurst=5
    OnFailure=campi_sos.service

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=$ROOT_DIR
    Restart=always
    RestartSec=3
    ExecStart=${ROOT_DIR}/board/${BOARD}/bin/nanomq start
    ExecStop=${ROOT_DIR}/board/${BOARD}/bin/nanomq stop
    TimeoutStartSec=3
    TimeoutStopSec=3

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE 2>&1 /dev/null
cp ${SRC_DIR}/$SERVICE $DST_DIR
systemctl daemon-reload
# systemctl enable $SERVICE
systemctl restart $SERVICE
systemctl status $SERVICE
journalctl -u $SERVICE --no-pager -n 10
echo "-------------------------------"
echo ""
echo "journalctl -u $SERVICE -f -n 100"
echo ""
echo "-------------------------------"
