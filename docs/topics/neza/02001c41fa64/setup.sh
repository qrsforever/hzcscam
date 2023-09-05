#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../../env.sh

CLIENTID=`basename $CUR_DIR`
PUB_TOPIC=cloud/${CLIENTID}/sensor/config

cat > /tmp/neza.json <<EOF
{
  "debug_mode": 1,
  "current_color": 1,
  "current_sensor": 1,
  "count": 0,
  "trigger_pulse": 0,
  "calm_step_ms": 20,
  "calm_down_ms": 120,
  "read_sleep_ms": 50
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
