#!/bin/bash

# git clone --depth 1 https://gitee.com/hzcsai_com/hzcscam.git

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)

ln -s ${TOP_DIR} /campi
mkdir -p /campi/runtime

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

# install service
/campi/scripts/install_nmq_service.sh
/campi/scripts/install_sys_service.sh
/campi/scripts/install_api_service.sh
/campi/scripts/install_cpi_service.sh

