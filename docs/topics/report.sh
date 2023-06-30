#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

cat > /tmp/about.json <<EOF
{
    "emq": true,
    "frp": true,
    "gst": true,
    "sys": true
}
EOF

if [[ x${ID} == x ]]
then
    CLOUD_REPORT=cloud/all/events/report
    __echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -m "{}"
else
    CLOUD_REPORT=cloud/${CLIENTID}/events/report
    __echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -f /tmp/about.json
fi
