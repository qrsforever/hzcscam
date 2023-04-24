#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file usb.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 21:53

from . import EventDetector

class UsbEventDetector(EventDetector):
    subsystem = 'usb'
    device_types = ['usb_device']

    def __init__(self, mqtt):
        super().__init__(mqtt)

    async def handle_event(self, device):
        print(device)
