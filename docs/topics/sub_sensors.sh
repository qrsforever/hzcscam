#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/env.sh

if [[ x$ID == x ]]
then
    ALL_TOPICS=campi/+/sensor/report
else
    ALL_TOPICS=campi/$ID/sensor/report
fi

printf "%12s %5s %5s %5s %5s %5s %5s %-20s\n" "id" "Count" "Pulse" "Check" "CalmS" "CalmD" "Read" "   Name"
mosquitto_sub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${ALL_TOPICS} -i mosquitto_sub_sensor --pretty -v | while read -r line
do
    topic=`echo $line | cut -d\  -f1`
    jdata=`echo $line | cut -d\  -f2-`
    cid=`echo $topic | cut -d\/ -f2`
    if [[ $cid == 02006602fe7b ]]
    then
        continue
    fi

    cname=$(cat ./neza/neza.txt | grep "$cid" | cut -d@ -f2)
    count=
    pulse=
    check=
    calms=
    calmd=
    sread=

    echo $jdata | jq | grep -E "\"count\"|trigger_|chkrnd_|calm_step_|calm_down_|read_sleep_" | while read -r payload
    do
        if [[ $payload =~ \"count.* ]]
        then
            count=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"trigger_.* ]]
        then
            pulse=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"chkrnd_.* ]]
        then
            check=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"calm_step_.* ]]
        then
            calms=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"calm_down_.* ]]
        then
            calmd=`echo $payload | cut -d: -f2 | sed s/\"//g`
        elif [[ $payload =~ \"read_sleep_.* ]]
        then
            sread=`echo $payload | cut -d: -f2 | sed s/\"//g`
            if [[ ${sread: -1} == "," ]]
            then
                sread=${sread%?}
            fi
            printf "%12s %5d %5d %5d %5d %5d %5d %20s\n" $cid ${count%?} ${pulse%?} ${check%?} ${calms%?} ${calmd%?} ${sread} $cname
        fi
    done
done
