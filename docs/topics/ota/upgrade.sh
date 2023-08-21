#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/../../../; pwd)

source ${CUR_DIR}/../env.sh

version_info_path=${TOP_DIR}/.ota/version_info.json
if [[ x$1 != x ]]
then
    version_info_path=${TOP_DIR}/.ota/version_info_${1}.json
fi

PUB_TOPIC=cloud/${CLIENTID}/ota/upgrade

__echo_run mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -q 2 -t ${PUB_TOPIC} -i mosquitto_pub_ota -f ${version_info_path}
