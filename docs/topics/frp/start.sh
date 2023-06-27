#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

port=7712

if [[ x$1 != x ]]
then
    port=$1
fi

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/frpc
CLOUD_REPORT=cloud/${CLIENTID}/events/report

cat > /tmp/frpc.json <<EOF
{
    "frpc_enable":true,
    "server_addr":"82.157.36.183",
    "server_port":7777,
    "remote_port":${port}
}
EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -d -f /tmp/frpc.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -m "{\"frp\": true}"
