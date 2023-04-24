#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 22:23


# from campi.core.atask import AsyncTask

# from pyudev import Context, Monitor
# from .usb import UsbEventDetector

# class SystemEventMonitor(object):
#     context = Context()
#     monitor = Monitor.from_netlink(context, source='udev')

#     def __init__(self):
#         self.usb = UsbEventDetector()
#         self.monitor.filter_by(subsystem='usb', device_type='usb_device')

#     @staticmethod
#     def main_loop():
#         pass

#     @staticmethod
#     def info(device):
#         s  = f'subsystem:{device.subsystem}, action:{device.action}, driver:{device.driver}, sys_name: {device.sys_name},'
#         s += f'device_type:{device.device_type}, device_path:{device.device_path}, device_node: {device.device_node}'
#         print(s)

import abc

class EventDetector(metaclass=abc.ABCMeta):
    subsystem = None
    device_types = [None]

    @abc.abstractmethod
    async def handle_event(self, device):
        pass

    def filter_by(self, monitor):
        for dt in self.device_types:
            monitor.filter_by(self.subsystem, dt)
        return self
