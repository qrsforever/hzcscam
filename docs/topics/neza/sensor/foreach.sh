#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

devices=(
)

for d in ${devices[@]}
do
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/sensor/config \
        -m "{\"current_color\": 0}"
done
