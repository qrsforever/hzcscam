#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

# CAMPI_REPORT=campi/+/events/#
if [[ x$ID == x ]]
then
    ALL_TOPICS=campi/+/events/report
else
    ALL_TOPICS=campi/$ID/events/report
fi

mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${ALL_TOPICS} -i mosquitto_sub --pretty -v | while read -r line
do
    topic=`echo $line | cut -d\  -f1`
    jdata=`echo $line | cut -d\  -f2-`
    echo "==================$topic==================="
    echo $jdata | jq
done
