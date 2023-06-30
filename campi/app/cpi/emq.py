#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file emq.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-30 10:40


import json
import os
from . import MessageHandler
from campi.topics import TCloud
from campi.constants import SENSOR_CONFIG_PATH


class EmqMessageHandler(MessageHandler):

    SNAME = 'campi_emq.service'

    def __init__(self):
        super().__init__([TCloud.EMQ_SENSOR])

    def get_info(self):
        config = {}
        if os.path.exists(SENSOR_CONFIG_PATH):
            with open(SENSOR_CONFIG_PATH, 'r') as fr:
                config['sensor'] = json.load(fr)
        return {"emq": config}

    def handle_message(self, topic, message):
        self.logger.debug(f'emq: {message}')

        if topic == TCloud.EMQ_SENSOR:
            pass
