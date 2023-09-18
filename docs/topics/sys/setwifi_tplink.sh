#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/net/setwifi
CLOUD_REPORT=cloud/${CLIENTID}/events/report

cat > /tmp/setwifi.json <<EOF
{
    "wifissid": "TP-LINK_ED3F",
    "password": "12345678910",
    "expbssid": "58:41:20:C1:ED:3F"
}
EOF

cat /tmp/setwifi.json

# not work
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/setwifi.json
