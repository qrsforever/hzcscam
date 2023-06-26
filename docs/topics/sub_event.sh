#!/bin/bash

CLIENTID=${CLIENTID:-0200519f3bab}
EMQX_HOST=${EMQX_HOST:-"aiot.hzcsdata.com"}
EMQX_PORT=${EMQX_PORT:-1883}
CAMPI_REPORT=campi/+/events/#

__echo_run()
{
    echo $*
    bash -c "$*"
}

__echo_run mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CAMPI_REPORT} # -C 1
