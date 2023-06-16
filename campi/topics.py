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

class TCloud:
    # EVENTS
    EVENTS_HEARTBEAT = f'campi/{ADDRESS}/events/heartbeat'
    EVENTS_ABOUT = f'campi/{ADDRESS}/events/about'

    # OTA
    OTA = f'cloud/{ADDRESS}/ota'
    UPGRADE_SUCESS = f'campi/{ADDRESS}/upgrade/success'
    UPGRADE_FAIL = f'campi/{ADDRESS}/upgrade/fail'

    # GST
    CAMERA_IMAGE = f'cloud/{ADDRESS}/camera/image'
    CAMERA_VIDEO = f'cloud/{ADDRESS}/camera/video'
    CAMERA_OVERLAY = f'cloud/{ADDRESS}/camera/overlay'
    CAMERA_RTMP = f'cloud/{ADDRESS}/camera/rtmp'
    CAMERA_CONFIG = f'campi/{ADDRESS}/camera/config'

    # FRP
    FRPC_CTRL = f'cloud/{ADDRESS}/frpc'

class TApis:
    SET_WIFI = '/apis/set_wifi'

class TUpgrade:
    BY_UDISK = 'upgrade/udisk'
    BY_OTA = 'upgrade/ota'
