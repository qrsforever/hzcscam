#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source /campi/_env

__echo_and_run() {
    echo "$*" >> /tmp/campi_gst_rtmp.log
    /bin/bash -c "$*"
}

# v4l2-ctl -d /dev/video0 --all
# gst-launch-1.0 v4l2src device=/dev/video0 io-mode=4 ! videoscale  ! video/x-raw, width=640, height=480, framerate=15/1 ! videoconvert  ! clockoverlay time-format="%H:%M:%S" halignment=right font-desc="normal 12" ! textoverlay text='12456789' valignment=top halignment=left font-desc="normal 12" ! autovideosink

if [[ ! -e /campi/runtime/gst_rtmp.env ]]
then
    cp ${SYSROOT}/etc/gst_rtmp.env /campi/runtime/gst_rtmp.env
fi

source /campi/runtime/gst_rtmp.env

INTERFACE=${INTERFACE:-eth0}
ADDRESS=$(cat /sys/class/net/${INTERFACE}/address | sed 's/://g')

FRAME_WIDTH=${FRAME_WIDTH:-640}
FRAME_HEIGHT=${FRAME_HEIGHT:-480}
FRAME_RATE=${FRAME_RATE:-15}

BRIGHTNESS=${BRIGHTNESS:-0}
CONTRAST=${CONTRAST:-0}
HUE=${HUE:-0}
SATURATION=${SATURATION:-0}

OVERLAY_FONT=${OVERLAY_FONT:-12}

if [[ x${VIDEO_DEVICE} != x ]]
then
    GSTSRC="v4l2src device=${VIDEO_DEVICE} io-mode=4 brightness=${BRIGHTNESS} contrast=${CONTRAST} hue=${HUE} saturation=${SATURATION} !"
else
    GSTSRC="videotestsrc !"
fi

if [[ x${RTMP_DOMAIN} != x ]]
then
    SRSOS_VHOST=${SRSOS_VHOST:-seg.300s}
    GSTSINK="x264enc bframes=0 speed-preset=veryfast key-int-max=30 ! flvmux streamable=true ! rtmpsink location=rtmp://${RTMP_DOMAIN}/live/${ADDRESS}?vhost=${SRSOS_VHOST}"
else
    GSTSINK="autovideosink"
fi

VIDEO_CONVERT=

if [[ x${FLIP_METHOD} != x ]]
then
    VIDEO_CONVERT="${VIDEO_CONVERT} videoflip method=${FLIP_METHOD} !"
fi

VIDEO_CONVERT="${VIDEO_CONVERT} videoscale ! video/x-raw, width=${FRAME_WIDTH}, height=${FRAME_HEIGHT}, framerate=${FRAME_RATE}/1 ! videoconvert !"

if [[ x${TIME_FORMAT} != x ]]
then
    TIME_HALIGNMENT=${TIME_HALIGNMENT:-right}
    TIME_VALIGNMENT=${TIME_VALIGNMENT:-top}
    VIDEO_CONVERT="${VIDEO_CONVERT} clockoverlay time-format=\"${TIME_FORMAT}\" halignment=${TIME_HALIGNMENT} valignment=${TIME_VALIGNMENT} font-desc=\"normal ${OVERLAY_FONT}\" !"
fi

if [[ x${TEXT_TITLE} != x ]]
then
    if [[ ${TEXT_TITLE} == auto ]]
    then
        TEXT_TITLE=${ADDRESS}
    fi
    TEXT_HALIGNMENT=${TEXT_HALIGNMENT:-left}
    TEXT_VALIGNMENT=${TEXT_VALIGNMENT:-top}
    VIDEO_CONVERT="${VIDEO_CONVERT} textoverlay text=\"${TEXT_TITLE}\" halignment=${TEXT_HALIGNMENT} valignment=${TEXT_VALIGNMENT} font-desc=\"normal ${OVERLAY_FONT}\" !"
fi

PLAY_TEST="http://101.42.139.3:30808/players/rtc_player.html?vhost=${SRSOS_VHOST}&ip=192.168.152.185&api=31985&app=live&stream=${ADDRESS}&autostart=true"

while (( 1 ))
do
    if [[ -e ${VIDEO_DEVICE} ]]
    then
        if [[ x${RTMP_DOMAIN} != x ]]
        then
            netok=$(ping -c 1 -W 2 ${RTMP_DOMAIN} 2>/dev/null | grep -o "received")
            if [[ x${netok} != x ]]
            then
                echo ${PLAY_TEST} > /tmp/campi_gst_rtmp.log
                __echo_and_run gst-launch-1.0 ${GSTSRC} ${VIDEO_CONVERT} ${GSTSINK}
            else
                echo "ping ${RTMP_DOMAIN} not received!"
            fi
        fi
    else
        echo "camera [${VIDEO_DEVICE}] is not exist!"
        # __echo_and_run gst-launch-1.0 ${GSTSRC} ${VIDEO_CONVERT} ${GSTSINK}
    fi
    sleep 5
done