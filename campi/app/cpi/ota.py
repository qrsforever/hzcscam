#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-08 23:12


from . import MessageHandler
from campi.topics import TCloud

class LoggerMessageHandler(MessageHandler):
    def __init__(self):
        super().__init__([TCloud.OTA])

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')
