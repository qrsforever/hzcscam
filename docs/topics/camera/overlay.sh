#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/camera/overlay
CLOUD_REPORT=cloud/${CLIENTID}/events/report

cat > /tmp/camera_overlay.json <<EOF
{
    "time_format": "\"%Y/%m/%d %H:%M:%S\"",
    "time_halignment": "right",
    "time_valignment": "top",
    "text_title": "auto",
    "text_halignmen": "left",
    "text_valignment": "top"
    "text_sensor_count": false,
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/camera_overlay.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -m "{\"gst\": true}"
