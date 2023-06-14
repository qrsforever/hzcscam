#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

SERVICE=campi_sos.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
TMP_DIR=/tmp/
DST_DIR=/etc/systemd/system/

cat > ${TMP_DIR}/$SERVICE <<EOF
[Unit]
    Description=System SOS
    Documentation=http://campi.hzcsai.com
    After=multi-user.target

[Service]
    Type=oneshot
    User=$USER
    Group=$USER
    UMask=0000
    WorkingDirectory=${ROOT_DIR}
    ExecStart=${ROOT_DIR}/board/${BOARD}/bin/sos_recovery.sh ${ROOT_DIR}

[Install]
    WantedBy=multi-user.target
EOF

chmod 644 ${TMP_DIR}/$SERVICE
mv ${TMP_DIR}/$SERVICE $DST_DIR

# systemctl stop $SERVICE 2>&1 > /dev/null
# systemctl daemon-reload
# systemctl enable $SERVICE
# systemctl restart $SERVICE
# systemctl status $SERVICE
# journalctl -u $SERVICE --no-pager -n 10
# echo "-------------------------------"
# echo ""
# echo "journalctl -u $SERVICE -f -n 100"
# echo ""
# echo "-------------------------------"
