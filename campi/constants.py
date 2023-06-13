#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file constants.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 22:53

import os

MAIN_PID = os.getpid()

BOARD = os.environ.get('BOARD', 'orangepi3-lts')
ADDRESS = os.environ.get('ADDRESS', '001122334466')
WS_ROOT = '/campi'
RUNTIME_PATH = f'{WS_ROOT}/runtime'
BOARD_PATH = f'{WS_ROOT}/board/{BOARD}'

## Archives

ARCHIVES_ROOT_PATH = '/var/campi/archives'
ARCHIVES_CURRENT_PATH = f'{ARCHIVES_ROOT_PATH}/current'

## Scripts

SCRIPT_OF_SET_WIFI = f'{BOARD_PATH}/bin/set_wifi.sh'
SCRIPT_OF_START_AP = f'{BOARD_PATH}/bin/hostap_start.sh'
SCRIPT_OF_STOP_AP = f'{BOARD_PATH}/bin/hostap_stop.sh'
SCRIPT_OF_START_UPGRADE = f'{BOARD_PATH}/bin/upgrade_start.sh'

## Network

WIFI_NM_CONF = f'{RUNTIME_PATH}/nmwifi.json'

## Upgrade

VERSION_APP_PATH = '/campi/version.txt'
VERSION_OTA_FILE = 'version_info.json'
