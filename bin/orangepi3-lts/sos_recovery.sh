#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

ARCHIVES_PATH=${ARCHIVES_PATH:-/var/campi/archives}

cp -arf ${ARCHIVES_PATH}/default ${ARCHIVES_PATH}/current

rm /campi
ln -s $ARCHIVES_PATH/$VALID_VERSION/campi /campi
for svc in ("nmq", "api", "gst", "sys")
do
    svc=campi_${svc}.service
    ret=$(systemctl is-active ${svc} | grep "active")
    if [[ x$ret == x ]]
    then
        echo "${svc} at $(date)" >> /tmp/campi_sos.log
        systemctl reset-failed  ${svc}
        systemctl restart ${svc}
    fi
done

exit 0
