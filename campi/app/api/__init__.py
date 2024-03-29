#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-26 15:08


import abc
import asyncio
from campi.core.amqtt import AsyncMqtt

import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class MessageHandler(metaclass=abc.ABCMeta):
    mqtt: AsyncMqtt = None
    callbacks1 = {}  # /topic/#
    callbacks2 = {}

    def __init__(self, topics):
        self.logger = logging.getLogger('campi')
        if MessageHandler.mqtt is None:
            mqtt = AsyncMqtt('campi', asyncio.get_running_loop())
            mqtt.message_callback = MessageHandler.dispatch_message
            mqtt.connect_sync()
            MessageHandler.mqtt = mqtt
        for topic in topics:
            cbs = self.callbacks1 if topic[-1] == '#' else self.callbacks2
            if topic not in cbs.keys():
                cbs[topic] = [self.handle_message]
            else:
                cbs[topic].append(self.handle_message)
            self.mqtt.subscribe(topic)
        print(self.callbacks1, self.callbacks2)

    @abc.abstractmethod
    def handle_message(self, topic, message):
        pass

    @classmethod
    def dispatch_message(cls, topic, message):
        for key, cbs in cls.callbacks1.items():
            if topic.startswith(key[:-2]):
                for cb in cbs:
                    cb(topic, message)

        for key, cbs in cls.callbacks2.items():
            if topic == key:
                for cb in cbs:
                    cb(topic, message)
