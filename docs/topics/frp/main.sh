#!/bin/bash

CLIENTID=${ID:-0200519f3bab}
EMQX_HOST=${EMQX_HOST:-"aiot.hzcsdata.com"}
EMQX_PORT=${EMQX_PORT:-1883}
PUB_TOPIC=cloud/${CLIENTID}/frpc
CLOUD_REPORT=cloud/${CLIENTID}/events/report

__echo_run()
{
    echo $*
    bash -c "$*"
}

__echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -f frpc.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -m "{\"frp\": true}"
