#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/camera/rtmp
CLOUD_REPORT=cloud/${CLIENTID}/events/report

sw=true

if [ x$1 == xfalse ] || [ x$1 == x0 ]
then
    sw=false
fi

cat > /tmp/camera_rtmp.json <<EOF
{
    "rtmp_enable": ${sw},
    "rtmp_domain": "srs.hzcsdata.com",
    "rtmp_room": "live",
    "rtmp_stream": "auto",
    "rtmp_vhost": "seg.300s"
}
EOF

# cat > /tmp/camera_rtmp.json <<EOF
# {
    # "rtmp_enable": ${sw},
    # "rtmp_domain": "aiot.hzcsdata.com",
    # "rtmp_room": "live",
    # "rtmp_stream": "auto",
    # "rtmp_vhost": ""
# }
# EOF

mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/camera_rtmp.json
sleep 1
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${CLOUD_REPORT} -i mosquitto_pub -m "{\"gst\": true}"
