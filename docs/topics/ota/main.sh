#!/bin/bash

CUR_DIR=$(cd $(dirname ${BASH_SOURCE[0]}); pwd)

CLIENTID=${CLIENTID:-0200519f3bab}
TOPIC=cloud/${CLIENTID}/ota
