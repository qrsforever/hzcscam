#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 22:53


from campi.core.atask import AsyncTask
from campi.app.sys import UMonitor


class NetEventDetector(UMonitor, AsyncTask):
    def __init__(self):
        super(NetEventDetector, self).__init__()
        self.monitor.filter_by(subsystem='net', device_type=None)

    async def run(self):
        for device in iter(self.monitor.poll, None):
            self.info(device)
