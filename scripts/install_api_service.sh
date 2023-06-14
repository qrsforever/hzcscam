#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

SERVICE=campi_api.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
TMP_DIR=${ROOT_DIR}/runtime
DST_DIR=/etc/systemd/system/

cat > ${TMP_DIR}/$SERVICE <<EOF
[Unit]
    Description=System Api for WebPage
    Documentation=http://campi.hzcsai.com
    StartLimitIntervalSec=120
    StartLimitBurst=5
    OnFailure=campi_sos.service

[Service]
    Type=simple
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=${ROOT_DIR}
    Environment="PYTHONPATH=${ROOT_DIR}"
    Restart=always
    RestartSec=3
    ExecStart=python3 ${ROOT_DIR}/campi/app/api
    TimeoutStartSec=3

[Install]
    WantedBy=multi-user.target
EOF

systemctl stop $SERVICE 2>&1 > /dev/null
mv ${TMP_DIR}/$SERVICE $DST_DIR
systemctl daemon-reload
# systemctl enable $SERVICE
# systemctl restart $SERVICE
# systemctl status $SERVICE
# journalctl -u $SERVICE --no-pager -n 10
# echo "-------------------------------"
# echo ""
# echo "journalctl -u $SERVICE -f -n 100"
# echo ""
# echo "-------------------------------"
