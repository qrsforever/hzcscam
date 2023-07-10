#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/sensor/config

cat > /tmp/neza.json <<EOF
{
  "debug_mode": 1,
  "current_color": 3,
  "current_sensor": 1,
  "count": 0,
  "trigger_pulse": 0,
  "calm_step_ms": 50,
  "calm_down_ms": 1500,
  "read_sleep_ms": 200
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
