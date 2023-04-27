#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sys.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:31


import multiprocessing
import subprocess
import json

from . import MessageHandler
from campi.topics import (
        tNetwork,
        tUsbDisk,
        tSystem,
        tApis)

from campi.constants import (
        SCRIPT_OF_START_AP,
        SCRIPT_OF_STOP_AP)

from campi.utils.net import util_wifi_connect


class SystemMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([
            tNetwork.ALL,
            tUsbDisk.ALL,
            tSystem.SHUTDOWN,
            tApis.SET_WIFI,
        ])

    def on_network_disconnect(self, message):

        def _start_wifiap():
            try:
                process = subprocess.Popen(
                        SCRIPT_OF_START_AP,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    self.logger.info(line.decode("utf-8").strip())
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {oerr}')

        multiprocessing.Process(target=_start_wifiap).start()

    def on_network_setwifi(self, message):
        jdata = json.loads(message)

        def _set_wifi():
            try:
                process = subprocess.Popen(
                        SCRIPT_OF_STOP_AP,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    self.logger.info(line.decode("utf-8").strip())
                util_wifi_connect(jdata['wifissid'], jdata['password'], 'wlan0')
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {oerr}')

        multiprocessing.Process(target=_set_wifi).start()

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == tSystem.SHUTDOWN:
            self.send_message('q')

        if topic == tNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)

        if topic == tApis.SET_WIFI:
            return self.on_network_setwifi(message)
