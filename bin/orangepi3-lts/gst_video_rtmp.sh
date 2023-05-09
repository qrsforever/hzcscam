#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

# http://101.42.139.3:30808/players/rtc_player.html?vhost=seg.300s&ip=192.168.152.185&api=31985&app=live&stream=02004a1a29a8

VIDEO_DVICE=/dev/video1
RTMP_DOMAIN=srs.hzcsdata.com
RTMP_STREAM=$(cat /sys/class/net/eth0/address | sed 's/://g')

while (( 1 ))
do
    if [[ -e ${VIDEO_DVICE} ]]
    then
        netok=$(ping -c 1 -W 2 ${RTMP_DOMAIN} 2>/dev/null | grep -o "received")
        if [[ x${netok} != x ]]
        then
            gst-launch-1.0 v4l2src device=${VIDEO_DVICE} io-mode=4 ! \
                video/x-raw, width=640, height=480, framerate=25/1 ! videoconvert ! \
                x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! \
                flvmux streamable=true ! rtmpsink location=rtmp://${RTMP_DOMAIN}/live/${RTMP_STREAM}?vhost=seg.300s
        fi
    fi
    sleep 5
done
