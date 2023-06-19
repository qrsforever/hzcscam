#!/bin/bash

# git clone --depth 1 https://gitee.com/hzcsai_com/hzcscam.git

FORCE_INSTALL=${1:-1}
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)
if [[ -L ${TOP_DIR} ]]
then
    TOP_DIR=$(readlink ${TOP_DIR})
    CUR_DIR=${TOP_DIR}/scripts
fi

source ${TOP_DIR}/_env

if [[ ! -d ${TOP_DIR}/runtime ]]
then
    mkdir -p ${TOP_DIR}/runtime
    cp ${TOP_DIR}/board/${BOARD}/etc/nmwifi.json ${TOP_DIR}/runtime/
    cp ${TOP_DIR}/board/${BOARD}/etc/gst_rtmp.env ${TOP_DIR}/runtime/
fi

gst_bin=$(command -v gst-launch-1.0)
if [[ x$gst_bin == x || ${FORCE_INSTALL} == 1 ]]
then
    systemctl stop systemd-resolved
    systemctl disable systemd-resolved
    systemctl mask systemd-resolved

    apt update
    apt install -y dnsmasq
    apt install -y python3-dev python3-pip libx264-dev libjpeg-dev v4l-utils
    apt install -y gstreamer1.0-tools gstreamer1.0-alsa \
         gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
         gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
         gstreamer1.0-libav gstreamer1.0-x
    apt install -y python3-gst-1.0

    pip3 install requests psutil pyudev paho-mqtt quart PyEmail cos-python-sdk-v5
fi

chmod +x ${TOP_DIR}/board/${BOARD}/bin/*

if [[ ! -L /campi ]]
then
    ln -s ${TOP_DIR} /campi
fi

# install service
for install_svc_script in `find ${CUR_DIR} -name "install_*_service.sh"`
do
    chmod +x ${install_svc_script}
    echo "install ${install_svc_script}"
    ${install_svc_script}
done

systemctl daemon-reload

${CUR_DIR}/setup_crontab.sh

LT=$(readlink /etc/localtime)
if [[ ${LT##*/} != Shanghai ]]
then
    rm -f /etc/localtime
    ln -snf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
    echo "Asia/Shanghai" > /etc/timezone
fi
