#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file topics.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-24 23:21

# from campi.utils.net import MAC
from campi.constants import ADDRESS

class TSystem:
    ALL = 'system/#'
    SHUTDOWN = 'system/shutdown'

class TNetwork:
    ALL = 'network/#'
    CONNECTED = 'network/connected'
    DISCONNECTED = 'network/disconnected'

class TUsbDisk:
    ALL = 'usbdisk/#'
    MOUNTED = 'usbdisk/mounted'
    UMOUNTED = 'usbdisk/umounted'

class TUsbCamera:
    ALL = 'camera/#'
    PLUGIN = 'camera/plugin'
    PLUGOUT = 'camera/plugout'

class TLogger:
    ALL = 'logger/#'
    DEBUG = 'logger/debug'
    INFO = 'logger/info'
    WARN = 'logger/warn'
    ERROR = 'logger/error'

    COLLECT = 'logger/collect'

class TCloud:
    # EVENTS
    EVENTS_HEARTBEAT = f'campi/{ADDRESS}/events/heartbeat'
    EVENTS_ABOUT = f'campi/{ADDRESS}/events/about'
    EVENTS_REPORT = 'cloud/all/events/report'
    EVENTS_CLOUD_REPORT = f'cloud/{ADDRESS}/events/report'
    EVENTS_CAMPI_REPORT = f'campi/{ADDRESS}/events/report'

    # OTA
    OTA_UPGRADE = f'cloud/{ADDRESS}/ota/upgrade'
    OTA_CONFIG = f'cloud/{ADDRESS}/ota/config'
    UPGRADE_REQUEST_ERROR = f'campi/{ADDRESS}/upgrade/request_error'
    UPGRADE_START = f'campi/{ADDRESS}/upgrade/start'
    UPGRADE_SUCESS = f'campi/{ADDRESS}/upgrade/success'
    UPGRADE_FAIL = f'campi/{ADDRESS}/upgrade/fail'

    # GST
    CAMERA_IMAGE = f'cloud/{ADDRESS}/camera/image'
    CAMERA_VIDEO = f'cloud/{ADDRESS}/camera/video'
    CAMERA_OVERLAY = f'cloud/{ADDRESS}/camera/overlay'
    CAMERA_RTMP = f'cloud/{ADDRESS}/camera/rtmp'
    CAMERA_CONFIG = f'campi/{ADDRESS}/camera/config'

    # FRP
    FRPC_CLOUD_CTRL = f'cloud/{ADDRESS}/frpc'

    # EMQ
    EMQ_SENSOR = f'cloud/{ADDRESS}/emq/sensor'

    # LOG
    LOGCAT_COLLECT = f'cloud/{ADDRESS}/log/collect'
    LOGCAT_MESSAGE = f'campi/{ADDRESS}/log/message'

class TApis:
    SET_WIFI = '/apis/set_wifi'

class TUpgrade:
    BY_UDISK = 'upgrade/udisk'
    BY_OTA = 'upgrade/ota'
    BY_AUTO = 'upgrade/auto'
