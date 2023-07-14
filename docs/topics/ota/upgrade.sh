#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/../../../; pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/ota/upgrade

__echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -f ${TOP_DIR}/.ota/version_info.json
