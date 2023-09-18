#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/net/setwifi
CLOUD_REPORT=cloud/${CLIENTID}/events/report

case "$1" in
    166)
        BSSID="B4:77:48:AC:3B:A6"
        ;;
    177)
        BSSID="B4:77:48:AC:2D:6E"
        ;;
    188)
        BSSID="20:C8:F7:63:EA:FE"
        ;;
    155)
        BSSID="B4:77:48:B4:0D:DC"
        ;;
    144)
        BSSID="20:F6:4E:B5:4A:48"
        ;;
    *)
        BSSID="$1"
esac

cat > /tmp/setwifi.json <<EOF
{
    "wifissid": "hzcsdata",
    "password": "Hzcsai@123",
    "expbssid": "${BSSID}"
}
EOF

cat /tmp/setwifi.json

# not work
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/setwifi.json
