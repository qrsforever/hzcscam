#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file constants.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 22:53

import os

MAIN_PID = os.getpid()

WS_ROOT = '/campi'
BOARD = os.environ.get('BOARD', 'orangepi3-lts')

## Scripts

SCRIPT_OF_SET_WIFI = f'{WS_ROOT}/board/{BOARD}/bin/set_wifi.sh'
SCRIPT_OF_START_AP = f'{WS_ROOT}/board/{BOARD}/bin/hostap_start.sh'
SCRIPT_OF_STOP_AP = f'{WS_ROOT}/board/{BOARD}/bin/hostap_stop.sh'

## Network

WIFI_NM_CONF = f'{WS_ROOT}/runtime/nmwifi.json'
