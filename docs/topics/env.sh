#!/bin/bash

CLIENTID=${ID:-0200519f3bab}
EMQX_HOST=${EMQX_HOST:-"aiot.hzcsdata.com"}
EMQX_PORT=${EMQX_PORT:-1883}

__echo_run()
{
    echo $*
    bash -c "$*"
}
