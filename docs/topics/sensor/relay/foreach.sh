#!/bin/bash

TOP_DIR=$(git rev-parse --show-toplevel)
source ${TOP_DIR}/docs/topics/env.sh

for d in ${SENSOR_RELAY_IDS[@]}
do
    echo "set $d"
    mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} \
        -u campi -P 123456 \
        -t cloud/${d}/sensor/config \
        -m "{\"trigger_pulse\": 1, \"calm_step_ms\":30, \"calm_down_ms\": 300, \"read_sleep_ms\": 50}"
done
