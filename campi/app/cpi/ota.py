#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-08 23:12


import subprocess

from . import MessageHandler
from campi.constants import ARCHIVES_ROOT_PATH
from campi.topics import TCloud
from campi.topics import TUpgrade

class OtaMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([TCloud.OTA, TUpgrade.BY_UDISK, TUpgrade.OTA])

    def _unzip_tarball(self, zip_path):
        try:
            subprocess.check_call(f'unzip -qo {zip_path} -d {ARCHIVES_ROOT_PATH}', shell=True)
            return 0
        except subprocess.CalledProcessError as err:
            return err.returncode
        except Exception:
            pass
        return -1

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == TUpgrade.BY_UDISK:
            # self.send_message()
            # if 0 != _unzip_tarball(message):
            return
                

        if topic == TCloud.OTA:
            pass
