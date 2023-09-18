#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

if [[ x$ID == x ]]
then
    ALL_TOPICS=campi/+/events/#
else
    ALL_TOPICS=campi/$ID/events/#
fi

printf "%12s %16s %20s %12s\t%-20s\n" "id" "gw      " "ip        " "version" "name"
mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${ALL_TOPICS} -i mosquitto_sub_all --pretty -v | while read -r line
do
    topic=`echo $line | cut -d\  -f1`
    jdata=`echo $line | cut -d\  -f2-`
    cid=`echo $topic | cut -d\/ -f2`
    if [[ $cid == 02006602fe7b ]]
    then
        continue
    fi
    cname=$(cat ./neza/neza.txt | grep "$cid" | cut -d@ -f2)
    ip=''
    gw=''
    ver=''
    echo $jdata | jq | grep -E "\"ip\"|gateway|software" | while read -r payload
    do
        if [[ $payload =~ \"ip.* ]]
        then
            ip=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"gateway.* ]]
        then
            gw=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"software.* ]]
        then
            ver=`echo $payload | cut -d: -f2 | sed s/\"//g`
            if [[ x$ip != x ]]
            then
                printf "%12s %16s %20s %12s\t%-20s\n" $cid ${gw%?} ${ip%?} ${ver%?} ${cname}
            fi
        fi
    done
done
