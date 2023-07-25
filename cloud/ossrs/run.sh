#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

docker run -dit --name srsos --network host \
    --volume ${CUR_DIR}/srs_rtmp.conf:/usr/local/srs/conf/srs_rtmp.conf \
    --volume ${CUR_DIR}/rtc_player.html:/usr/local/srs/objs/nginx/html/players/rtc_player.html \
    hzcsk8s.io/frepai/srs_rtc \
    /usr/local/srs/objs/srs -c /usr/local/srs/conf/srs_rtmp.conf

