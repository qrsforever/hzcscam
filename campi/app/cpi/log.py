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
from campi.utils.oss import coss3_put, coss3_domain

class LogMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([TLogger.ALL, TCloud.LOGCAT_COLLECT])

    def _do_logcat(self, config):
        try:
            since = config.get('since', 'today')
            lines = config.get('lines', 0)
            dmesg = config.get('dmesg', True)
            process = subprocess.Popen(
                    "%s --since '%s' --lines %d %s" % (SCRIPT_OF_LOGCAT, since, lines, '--dmesg' if dmesg else ''),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True)
            for line in process.stdout:
                line = line.decode("utf-8").strip()
                if 'logzip' in line:
                    zip_path = line.split(':')[1]
                    coss3_put(zip_path, [os.path.dirname(zip_path), OSS_LOGCAT_PATH])
                    os.unlink(zip_path)
                    config['logzip'] = f'{coss3_domain}/{OSS_LOGCAT_PATH}/{os.path.basename(zip_path)}'
                else:
                    self.logger.info(f'{line}')
        except subprocess.CalledProcessError as cerr:
            config['logzip'] = f'{cerr}'
            self.logger.error(f'set wifi err[{SCRIPT_OF_LOGCAT}]: {cerr}')
        except Exception as oerr:
            config['logzip'] = f'{oerr}'
            self.logger.error(f'set wifi err[{SCRIPT_OF_LOGCAT}]: {oerr}')

        self.send_message(TCloud.LOGCAT_MESSAGE, config)

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
            if topic == TCloud.LOGCAT_COLLECT:
                return self._do_logcat(json.loads(message))
