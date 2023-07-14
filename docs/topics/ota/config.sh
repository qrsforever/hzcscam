#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/../../../; pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/ota/config

cat > /tmp/neza.json <<EOF
{
    "upgrade_server": "http://aiot.hzcsdata.com:30082"
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/neza.json
