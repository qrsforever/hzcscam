#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

FORCE_INSTALL=0
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)

source ${TOP_DIR}/_env

args="-f -n 100"

for svc in ${CAMPI_ORDER_SVCS[@]}
do
    args="${args} -u campi_${svc}.service"
done

journalctl ${args
