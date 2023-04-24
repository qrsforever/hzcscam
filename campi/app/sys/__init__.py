#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 22:23


import abc

class EventDetector(metaclass=abc.ABCMeta):
    subsystem = None
    device_types = [None]

    def __init__(self, mqtt):
        self.mqtt = mqtt

    @abc.abstractmethod
    async def handle_event(self, device):
        pass

    def filter_by(self, monitor):
        for dt in self.device_types:
            monitor.filter_by(self.subsystem, dt)
        return self
