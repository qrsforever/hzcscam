#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __init__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 22:23


from pyudev import Context, Monitor


class UMonitor(object):
    context = Context()

    def __init__(self):
        self.monitor = Monitor.from_netlink(self.context)

    def info(self, device):
        s  = f'subsystem:{device.subsystem}, action:{device.action}, driver:{device.driver}, sys_name: {device.sys_name},'
        s += f'device_type:{device.device_type}, device_path:{device.device_path}, device_node: {device.device_node}'
        print(s)
