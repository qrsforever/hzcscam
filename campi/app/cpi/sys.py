#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sys.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:31


import multiprocessing
import subprocess

from . import MessageHandler
from campi.topics import (
        tNetwork,
        tUsbDisk,
        tSystem)

from campi.constants import SCRIPT_OF_START_AP


class SystemMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([
            tNetwork.ALL,
            tUsbDisk.ALL,
            tSystem.SHUTDOWN
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

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == tSystem.SHUTDOWN:
            self.send_message('q')

        if topic == tNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)
