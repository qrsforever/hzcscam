#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

devices=(
    02006893436a
    02007cd6f4d4
    02005ad1dd6c
    02009aa1a989
    0200b27901c5
    02007d149ee3
    020029a93773
    020057b3d11a
    0200ccb29ac7
    02001c5293a6
)

for d in ${devices[@]}
do
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/sensor/config \
        -m "{\"trigger_pulse\": 1, \"calm_step_ms\":30, \"calm_down_ms\": 300, \"read_sleep_ms\": 50}"
done
