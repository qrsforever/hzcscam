#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

for d in ${SENSOR_ALL_IDS[@]}
do
    echo "set $d"
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/camera/image \
        -m "{\"frame_width\": 640, \"frame_height\": 480}"

    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/camera/video \
        -m "{\"video_speed_preset\": \"ultrafast\", \"video_bitrate\": 600}"
done
