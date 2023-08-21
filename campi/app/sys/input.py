#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file input.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-15 20:12


from . import EventDetector
from campi.topics import TUsbCamera
from campi.utils.shell import utils_syscall


class InputEventDetector(EventDetector):
    subsystem = 'input'
    device_types = []

    def __init__(self, mqtt):
        super().__init__(mqtt)

    def filter_by(self, monitor):
        monitor.filter_by(self.subsystem)
        return self

    def get_camera_device(self):
        return utils_syscall("v4l2-ctl --list-devices | grep usb-1 -A1 | grep video | awk 'NR==1 {print $1}'")

    def on_plugin(self, device_path, sys_name):
        # check usb camera
        self.mqtt.logi(f'plugin: {device_path} {sys_name}')
        if not self.camera:
            camera = self.get_camera_device()
            if camera:
                self.mqtt.publish(TUsbCamera.PLUGIN, camera)
                self.camera = camera

    def on_plugout(self, device_path, sys_name):
        self.mqtt.logi(f'plugout: {device_path} {sys_name}')
        if self.camera:
            camera = self.get_camera_device()
            if not camera:
                self.mqtt.publish(TUsbCamera.PLUGOUT, self.camera)
                self.camera = ''

    async def on_setup(self):
        self.camera = self.get_camera_device()
        if self.camera:
            self.mqtt.publish(TUsbCamera.PLUGIN, self.camera, qos=2)

    async def handle_event(self, device):
        if device.action == 'add':
            return self.on_plugin(device.device_path, device.sys_name)
        elif device.action == 'remove':
            return self.on_plugout(device.device_path, device.sys_name)
