#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

if [[ -z $1 ]]
then
    cat > /tmp/about.json <<EOF
{
    "emq": true,
    "frp": true,
    "gst": true,
    "ota": true,
    "sys": true
}
EOF
else
    cat > /tmp/about.json <<EOF
{
    "$1": true
}
EOF
fi

if [[ x${ID} == x ]]
then
    CLOUD_REPORT=cloud/all/events/report
    __echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -i mosquitto_pub -f /tmp/about.json
else
    CLOUD_REPORT=cloud/${CLIENTID}/events/report
    __echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -i mosquitto_pub -f /tmp/about.json
fi
