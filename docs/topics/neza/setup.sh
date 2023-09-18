#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(git rev-parse --show-toplevel)
MQTT_DIR=${TOP_DIR}/docs/topics
source ${MQTT_DIR}/../../env.sh

CLIENTID=`basename $CUR_DIR`
PUB_TOPIC=cloud/${CLIENTID}/sensor/config

cat > /tmp/neza.json <<EOF
{
  "debug_mode": 1,
  "current_color": 1,
  "current_sensor": 1,
  "count": 0,
  "trigger_pulse": 1,
  "calm_step_ms": 30,
  "calm_down_ms": 300,
  "read_sleep_ms": 100
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
