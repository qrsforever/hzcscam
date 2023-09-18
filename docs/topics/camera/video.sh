#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/camera/video
CLOUD_REPORT=cloud/${CLIENTID}/events/report

# tune: none zerolatency stillimage fastdecode
# speed-preset: none, ultrafast superfast veryfast faster fast medium slow slower veryslow
# pass: none cbr quant qual pass1 pass2 pass3
# profile: none baseline main high
# video_quantizer: 0 - 50
cat > /tmp/camera_video.json <<EOF
{
    "video_bitrate": 600,
    "video_quantizer": 30,
    "video_tune": "zerolatency",
    "video_speed_preset": "ultrafast",
    "video_pass": "qual",
    "video_profile": "main"
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/camera_video.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -i mosquitto_pub -m "{\"gst\": true}"
