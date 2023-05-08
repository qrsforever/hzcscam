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
        SCRIPT_OF_SET_WIFI,
        SCRIPT_OF_START_AP,
        SCRIPT_OF_STOP_AP)

from campi.utils.net import (
        util_get_mac,
        util_get_lanip,
        util_get_netip,
        util_send_mail)


class SystemMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([
            tNetwork.ALL,
            tUsbDisk.ALL,
            tSystem.SHUTDOWN,
            tApis.SET_WIFI,
        ])

        self.wifiap_running = False

    def on_network_connected(self, message):
        # TODO
        self.wifiap_running = False

        util_send_mail(json.dumps({
            'mac': util_get_mac(),
            'lanip': util_get_lanip(),
            'netip': util_get_netip()
        }))

    def on_network_disconnect(self, message):
        if self.wifiap_running:
            self.logger.info('hostapd already running')
            return
        self.wifiap_running = True

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
                self.wifiap_running = False
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {oerr}')

            try:
                process = subprocess.Popen(
                        f'{SCRIPT_OF_SET_WIFI} {jdata["wifissid"]} {jdata["password"]}',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    self.logger.info(line.decode("utf-8").strip())
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {oerr}')

        multiprocessing.Process(target=_set_wifi).start()

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == tSystem.SHUTDOWN:
            self.send_message('q')

        if topic == tNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)

        if topic == tNetwork.CONNECTED:
            return self.on_network_connected(message)

        if topic == tApis.SET_WIFI:
            return self.on_network_setwifi(message)
