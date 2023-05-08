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

SCRIPT_OF_SET_WIFI = f'{WS_ROOT}/bin/{BOARD}/set_wifi.sh'
SCRIPT_OF_START_AP = f'{WS_ROOT}/bin/{BOARD}/hostap_start.sh'
SCRIPT_OF_STOP_AP = f'{WS_ROOT}/bin/{BOARD}/hostap_stop.sh'
