#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/sensor/config

cat > /tmp/neza.json <<EOF
{
  "current_color": 1,
  "current_sensor": 1,
  "count": 0,
  "trigger_pulse": 1,
  "calm_step_ms": 20,
  "calm_down_ms": 200,
  "read_sleep_ms": 300
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
