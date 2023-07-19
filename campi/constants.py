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

## Services
SVC_API = 'campi_api.service'
SVC_GST = 'campi_gst.service'
SVC_NMQ = 'campi_nmq.service'
SVC_SYS = 'campi_sys.service'
SVC_SOS = 'campi_sos.service'
SVC_FRP = 'campi_frp.service'
SVC_EMQ = 'campi_emq.service'
SVC_CPI = 'campi_cpi.service'

## Scripts

SCRIPT_OF_SET_WIFI = f'{BOARD_PATH}/bin/set_wifi.sh'
SCRIPT_OF_START_AP = f'{BOARD_PATH}/bin/hostap_start.sh'
SCRIPT_OF_STOP_AP = f'{BOARD_PATH}/bin/hostap_stop.sh'
SCRIPT_OF_START_UPGRADE = f'{BOARD_PATH}/bin/upgrade_start.sh'
SCRIPT_OF_LOGCAT = f'{BOARD_PATH}/bin/logcat_start.sh'

## Network

WIFI_NM_FILE = 'nmwifi.json'
WIFI_NM_CONF = f'{RUNTIME_PATH}/{WIFI_NM_FILE}'

## Upgrade

OTA_UPGRADE_CONF = f'{RUNTIME_PATH}/ota.json'
VERSION_APP_PATH = '/campi/version.txt'
VERSION_OTA_FILE = 'version_info.json'
APP_VERSION = os.environ.get('APP_VERSION', '1.0.0')

## Gst

GST_CONFIG_PATH = f'{RUNTIME_PATH}/gst_rtmp.env'
GST_CAMERA_PROP = f'{RUNTIME_PATH}/camera_props.json'

## FRP

FRP_CONFIG_PATH = f'{RUNTIME_PATH}/frpc.ini'

## LOG

OSS_LOGCAT_PATH = f'logcat/{ADDRESS}'

## EMQ

SENSOR_CONFIG_PATH = f'{RUNTIME_PATH}/emq_sensor.json'
