#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file log.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:55


from . import MessageHandler
from campi.topics import TLogger

class LoggerMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([TLogger.ALL])

    def handle_message(self, topic, message):
        if topic == TLogger.INFO:
            self.logger.info(message)
        elif topic == TLogger.WARN:
            self.logger.warn(message)
        elif topic == TLogger.ERROR:
            self.logger.error(message)
        else:
            self.logger.debug(message)
