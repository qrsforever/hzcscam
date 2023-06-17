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

## Scripts

SCRIPT_OF_SET_WIFI = f'{BOARD_PATH}/bin/set_wifi.sh'
SCRIPT_OF_START_AP = f'{BOARD_PATH}/bin/hostap_start.sh'
SCRIPT_OF_STOP_AP = f'{BOARD_PATH}/bin/hostap_stop.sh'
SCRIPT_OF_START_UPGRADE = f'{BOARD_PATH}/bin/upgrade_start.sh'

## Network

WIFI_NM_FILE = 'nmwifi.json'
WIFI_NM_CONF = f'{RUNTIME_PATH}/{WIFI_NM_FILE}'

## Upgrade

VERSION_APP_PATH = '/campi/version.txt'
VERSION_OTA_FILE = 'version_info.json'
APP_VERSION = '1.0.0'

with open(VERSION_APP_PATH, 'r') as fr:
    APP_VERSION = fr.read().strip()

## Gst

GST_CONFIG_PATH = f'{RUNTIME_PATH}/gst_rtmp.env'
GST_CAMERA_PROP = f'{RUNTIME_PATH}/camera_props.json'

## FRP

FRP_CONFIG_PATH = '/tmp/frpc.ini'
