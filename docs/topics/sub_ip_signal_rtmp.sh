#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

if [[ x$ID == x ]]
then
    ALL_TOPICS=campi/+/events/#
else
    ALL_TOPICS=campi/$ID/events/#
fi

printf "%s, %16s %6s %6s %6s\n" "         id" "      address     " "  ss" "    ping" "rtmp"
mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${ALL_TOPICS} -i mosquitto_sub_all --pretty -v | while read -r line
do
    topic=`echo $line | cut -d\  -f1`
    jdata=`echo $line | cut -d\  -f2-`
    cid=`echo $topic | cut -d\/ -f2`
    ip=''
    ss=''
    pt=''
    re=''
    echo $jdata | jq | grep -E "\"ip\"|signal_strength|ping_time_ms|rtmp_enable" | while read -r payload
    do
        if [[ $payload =~ \"ip.* ]]
        then
            ip=`echo $payload | cut -d: -f2`
        elif [[ $payload =~ \"signal_.* ]]
        then
            ss=`echo $payload | cut -d: -f2`
        elif [[ $payload =~ \"ping_.* ]]
        then
            pt=`echo $payload | cut -d: -f2`
        elif [[ $payload =~ \"rtmp_.* ]]
        then
            re=`echo $payload | cut -d: -f2`
            if [[ x$ip != x ]]
            then
                printf "%s, %16s %6s %8s %-8s\n" $cid $ip $ss $pt $re
            fi
        fi
    done
done
