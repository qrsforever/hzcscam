#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

source ${CUR_DIR}/../env.sh

PUB_TOPIC=cloud/${CLIENTID}/net/setwifi
CLOUD_REPORT=cloud/${CLIENTID}/events/report

case "$1" in
    ED3F)
        WSSID="TP-LINK_ED3F"
        BSSID="58:41:20:C1:ED:3F"
        ;;
    F069)
        WSSID="TP-LINK_F069"
        BSSID="58:41:20:C1:F0:69"
        ;;
    *)
        WSSID="TP-LINK_ED3F"
        BSSID="58:41:20:C1:ED:3F"
esac

  
cat > /tmp/setwifi.json <<EOF
{
    "wifissid": "${WSSID}",
    "password": "12345678910",
    "expbssid": "${BSSID}"
}
EOF

cat /tmp/setwifi.json

# not work
mosquitto_pub -h ${EMQX_HOST} -p ${EMQX_PORT} -u campi -P 123456 -t ${PUB_TOPIC} -i mosquitto_pub -d -f /tmp/setwifi.json
