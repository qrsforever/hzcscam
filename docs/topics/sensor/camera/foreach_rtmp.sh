#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

sw=true
if [ x$1 == xfalse ] || [ x$1 == x0 ]
then
    sw=false
fi

for d in ${SENSOR_CAMERA_IDS[@]}
do
    echo "set $d"
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/camera/rtmp \
        -m "{\"rtmp_enable\": ${sw}, \"rtmp_vhost\": \"seg.900s\"}"
done
