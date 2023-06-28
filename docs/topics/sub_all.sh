#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

# CAMPI_REPORT=campi/+/events/#
ALL_TOPICS=campi/#

__echo_run mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${ALL_TOPICS} -i mosquitto_sub --pretty -v
