#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file topics.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-24 23:21

# from campi.utils.net import MAC


class tSystem:
    ALL = '/system/#'
    SHUTDOWN = '/system/shutdown'


class tNetwork:
    ALL = '/network/#'
    CONNECTED = '/network/connected'
    DISCONNECTED = '/network/disconnected'


class tUsbDisk:
    ALL = '/usbdisk/#'
    MOUNTED = '/usbdisk/mounted'
    UMOUNTED = '/usbdisk/umounted'


class tLogger:
    ALL = '/logger/#'
    DEBUG = '/logger/debug'
    INFO = '/logger/info'
    WARN = '/logger/warn'
    ERROR = '/logger/error'


class tApis:
    SET_WIFI = '/apis/set_wifi'
