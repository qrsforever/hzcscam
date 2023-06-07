#!/bin/bash

# git clone --depth 1 https://gitee.com/hzcsai_com/hzcscam.git

FORCE_INSTALL=0
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)

rm -rf /campi
ln -s ${TOP_DIR} /campi

source /campi/_env

mkdir -p /campi/runtime

cp ${SYSROOT}/etc/nmwifi.json /campi/runtime
cp ${SYSROOT}/etc/gst_rtmp.env /campi/runtime

gst_bin=$(command -v gst-launch-1.0)
if [[ x$gst_bin == 1 || ${FORCE_INSTALL} == 1 ]]
then
    systemctl stop systemd-resolved
    systemctl disable systemd-resolved
    systemctl mask systemd-resolved

    apt update 
    apt install -y dnsmasq
    apt install -y python3-dev python3-pip libx264-dev libjpeg-dev
    apt install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav
    apt install -y python3-gst-1.0

    pip3 install pyudev paho-mqtt quart PyEmail
fi

# install service
for svc in ${CAMPI_ORDER_SVCS[@]}
do
    /campi/scripts/install_${svc}_service.sh
done
