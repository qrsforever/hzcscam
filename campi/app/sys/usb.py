#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file usb.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 21:53


from campi.core.atask import AsyncTask
from campi.app.sys import UMonitor


class UsbEventDetector(UMonitor, AsyncTask):
    def __init__(self):
        super(UsbEventDetector, self).__init__()
        self.monitor.filter_by(subsystem='usb', device_type='usb_device')

    async def run(self):
        for device in iter(self.monitor.poll, None):
            self.info(device)
