#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

SERVICE=campi_boot.service

USER=root
ROOT_DIR=/campi

BOARD=$(cat /etc/orangepi-release | grep BOARD= | cut -d= -f2)
TMP_DIR=/tmp/
DST_DIR=/etc/systemd/system/

cat > ${TMP_DIR}/$SERVICE <<EOF
[Unit]
    Description=System Boot Service
    Documentation=http://campi.hzcsai.com
    # OnFailure=/usr/local/bin/campi_safe_run.sh

[Service]
    Type=oneshot
    User=$USER
    Group=$USER
    UMask=0000
    ExecStart=${ROOT_DIR}/board/${BOARD}/bin/sys_onboot.sh

[Install]
    WantedBy=multi-user.target
EOF

chmod 644 ${TMP_DIR}/$ERVICE
mv ${TMP_DIR}/$SERVICE $DST_DIR
