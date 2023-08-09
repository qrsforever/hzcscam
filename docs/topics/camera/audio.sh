#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/camera/audio
CLOUD_REPORT=cloud/${CLIENTID}/events/report

sw=true
if [ x$1 == xfalse ] || [ x$1 == x0 ]
then
    sw=false
fi

cat > /tmp/camera_audio.json <<EOF
{
    "audio_enable": $sw,
    "audio_device": "hw:3,0",
    "audio_rate": 44100,
    "audio_channels": 1
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/camera_audio.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -i mosquitto_pub -m "{\"gst\": true}"
