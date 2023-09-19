#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

devices=(
    02001433f69e
    0200acfb85cf
    020025caf79a
    0200483d86b8
    020021c51db8
    020030793c0c
    02009d9dfd23
    020094d0a425
    02004d3aee9c
    02003cf0c324
    02003814c4c8
)

for d in ${devices[@]}
do
    echo "set $d"
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/camera/image \
        -m "{\"frame_width\": 640, \"frame_height\": 480}"
done
