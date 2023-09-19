#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

CLIENTID=${ID:-0200519f3bab}
EMQX_HOST=${EMQX_HOST:-"aiot.hzcsdata.com"}
EMQX_PORT=${EMQX_PORT:-1883}

__echo_run()
{
    echo $*
    bash -c "$*"
}

SENSOR_ALL_IDS=$(cat $CUR_DIR/neza/neza.txt | cut -d\  -f1)
SENSOR_CAMERA_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "相机" | cut -d\  -f1)
SENSOR_BAROCEPTOR_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "气压" | cut -d\  -f1)
SENSOR_PHOTOELECTRIC_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "光电" | cut -d\  -f1)
SENSOR_RELAY_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "继电器" | cut -d\  -f1)
SENSOR_VIBRATE_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "振动" | cut -d\  -f1)
SENSOR_METAL_IDS=$(cat $CUR_DIR/neza/neza.txt | grep "金属" | cut -d\  -f1)
