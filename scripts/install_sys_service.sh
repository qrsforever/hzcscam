#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

SERVICE=campi_sys.service

USER=root
ROOT_DIR=/campi

ADDRESS=$(cat /sys/class/net/eth0/address | sed 's/://g')
BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
TMP_DIR=/tmp/
DST_DIR=/etc/systemd/system/

cat > ${TMP_DIR}/$SERVICE <<EOF
[Unit]
    Description=System Monitor Event
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
    Environment="BOARD=${BOARD}"
    Environment="ADDRESS=${ADDRESS}"
    Restart=always
    RestartSec=5
    ExecStart=python3 ${ROOT_DIR}/campi/app/sys
    TimeoutStartSec=3

[Install]
    WantedBy=multi-user.target
EOF

chmod 644 ${TMP_DIR}/$SERVICE
mv ${TMP_DIR}/$SERVICE $DST_DIR

# systemctl stop $SERVICE 2>&1 > /dev/null
# systemctl daemon-reload
# # systemctl enable $SERVICE
# systemctl restart $SERVICE
# systemctl status $SERVICE
# # journalctl -u $SERVICE --no-pager -n 10
# echo "-------------------------------"
# echo ""
# echo "journalctl -u $SERVICE -f -n 100"
# echo ""
# echo "-------------------------------"
