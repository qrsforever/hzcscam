#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file input.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-15 20:12


import os
from . import EventDetector
from campi.topics import TUsbCamera


class InputEventDetector(EventDetector):
    subsystem = 'input'
    device_types = []

    def __init__(self, mqtt):
        super().__init__(mqtt)
        self.devices = []

    def filter_by(self, monitor):
        monitor.filter_by(self.subsystem)
        return self

    def on_plugin(self, device_path, sys_name):
        # check usb camera
        self.mqtt.logi(f'plugin: {device_path} {sys_name}')
        if sys_name not in self.devices:
            self.devices.append(sys_name)
        if os.path.exists('/dev/video1'):
            self.mqtt.publish(TUsbCamera.PLUGIN, '/dev/video1')

    def on_plugout(self, device_path, sys_name):
        self.mqtt.logi(f'plugout: {device_path} {sys_name}')
        if sys_name in self.devices:
            if not os.path.exists('/dev/video1'):
                self.mqtt.publish(TUsbCamera.PLUGOUT, '/dev/video1')
            self.devices.remove(sys_name)

    async def handle_event(self, device):
        if device.action == 'add':
            return self.on_plugin(device.device_path, device.sys_name)
        elif device.action == 'remove':
            return self.on_plugout(device.device_path, device.sys_name)
