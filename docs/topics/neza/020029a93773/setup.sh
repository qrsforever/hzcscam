#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../../env.sh

CLIENTID=020029a93773
PUB_TOPIC=cloud/${CLIENTID}/sensor/config

cat > /tmp/neza.json <<EOF
{
  "debug_mode": 1,
  "current_color": 1,
  "current_sensor": 1,
  "count": 0,
  "trigger_pulse": 1,
  "calm_step_ms": 30,
  "calm_down_ms": 100,
  "read_sleep_ms": 100
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
