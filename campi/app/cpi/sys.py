#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sys.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:31


from . import MessageHandler
from campi.topics import tNetwork
from campi.topics import tUsbDisk
from campi.constants import SCRIPT_OF_START_AP

import multiprocessing
import subprocess


class SystemMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([
            tNetwork.ALL,
            tUsbDisk.ALL
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
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}: {cerr}')
            except Exception as err:
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}: {err}')

        multiprocessing.Process(target=_start_wifiap).start()

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')
        if topic == tNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)
