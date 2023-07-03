#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/camera/image
CLOUD_REPORT=cloud/${CLIENTID}/events/report

# flip_method: "" or "vertical-flip" or "horizontal-flip"
cat > /tmp/camera_image.json <<EOF
{
    "frame_width": 640,
    "frame_height": 480,
    "frame_rate": 15,
    "brightness": 100,
    "contrast": 50,
    "hue": 50,
    "saturation":50,
    "flip_method": ""
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/camera_image.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -m "{\"gst\": true}"
