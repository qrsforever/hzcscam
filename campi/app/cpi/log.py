#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file log.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:55

import subprocess
import json
import os
from . import MessageHandler
from campi.topics import TLogger
from campi.topics import TCloud
from campi.constants import SCRIPT_OF_LOGCAT, OSS_LOGCAT_PATH
from campi.utils.oss import coss3_put

class LoggerMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([TLogger.ALL, TCloud.LOGCAT_CTRL])

    def _do_logcat(self, config):
        try:
            process = subprocess.Popen(
                    f'{SCRIPT_OF_LOGCAT}',
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                if 'logzip' in line:
                    zip_path = line.split(':')[1]
                    coss3_put(zip_path, [os.path.dirname(zip_path), OSS_LOGCAT_PATH])
        except subprocess.CalledProcessError as cerr:
            self.logger.error(f'set wifi err[{SCRIPT_OF_LOGCAT}]: {cerr}')
        except Exception as oerr:
            self.logger.error(f'set wifi err[{SCRIPT_OF_LOGCAT}]: {oerr}')

    def handle_message(self, topic, message):
        if topic == TLogger.INFO:
            self.logger.info(message)
        elif topic == TLogger.WARN:
            self.logger.warn(message)
        elif topic == TLogger.ERROR:
            self.logger.error(message)
        elif topic == TLogger.DEBUG:
            self.logger.debug(message)
        else:
            if topic == TCloud.LOGCAT_CTRL:
                return self._do_logcat(json.loads(message))
