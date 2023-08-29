#!/bin/bash

# git clone --depth 1 https://gitee.com/hzcsai_com/hzcscam.git

FORCE_INSTALL=${1:-0}
CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)
TOP_DIR=$(cd ${CUR_DIR}/..; pwd)
if [[ -L ${TOP_DIR} ]]
then
    TOP_DIR=$(readlink ${TOP_DIR})
    CUR_DIR=${TOP_DIR}/scripts
fi

source ${TOP_DIR}/_env

[[ ! -d ${TOP_DIR}/runtime/logs ]] &&  mkdir -p ${TOP_DIR}/runtime/logs

[ ! -f ${TOP_DIR}/runtime/nmwifi.json ] && cp ${TOP_DIR}/board/${BOARD}/etc/nmwifi.json ${TOP_DIR}/runtime/nmwifi.json
[ ! -f ${TOP_DIR}/runtime/gst.json ] && cp ${TOP_DIR}/board/${BOARD}/etc/gst.json ${TOP_DIR}/runtime/gst.json
[ ! -f ${TOP_DIR}/runtime/gst_rtmp.env ] && cp ${TOP_DIR}/board/${BOARD}/etc/gst_rtmp.env ${TOP_DIR}/runtime/gst_rtmp.env

__pip_install()
{
    if [[ -z $2 ]]
    then
        lib=$1
    fi
    check=`python3 -c "import $lib" 2>&1`
    if [[ x$check != x ]]
    then
        pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn $1
    fi
}

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
    pip3 install -i https://pypi.tuna.tsinghua.edu.cn/simple \
        --trusted-host pypi.tuna.tsinghua.edu.cn \
        requests psutil pyudev paho-mqtt quart PyEmail
    __pip_install requests
    __pip_install psutil
    __pip_install pyudev
    __pip_install quart
    __pip_install paho-mqtt paho.mqtt
    __pip_install PyEmail smtplib
    __pip_install cos-python-sdk-v5
fi

chmod +x ${TOP_DIR}/board/${BOARD}/bin/*

if [[ ! -L /campi ]]
then
    ln -s ${TOP_DIR} /campi
fi

ARCHIVES_PATH=${ARCHIVES_PATH:-/var/campi/archives}
if [[ ! -d ${ARCHIVES_PATH} ]]
then
    mkdir -p ${ARCHIVES_PATH} 
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

# not work, see v4l rules
# cp ${TOP_DIR}/board/${BOARD}/etc/50-usb-camera.rules /etc/udev/rules.d/50-usb-camera.rules

echo "${ADDRESS}" > /etc/hostname
