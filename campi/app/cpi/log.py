#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file log.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:55


from . import MessageHandler
from campi.topics import tLogger

class LoggerMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([tLogger.ALL])

    def handle_message(self, topic, message):
        if topic == tLogger.INFO:
            self.logger.info(message)
        elif topic == tLogger.WARN:
            self.logger.warn(message)
        elif topic == tLogger.ERROR:
            self.logger.error(message)
        else:
            self.logger.debug(message)
