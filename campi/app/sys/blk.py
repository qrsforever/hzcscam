#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file blk.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 18:14


from campi.core.atask import AsyncTask
from campi.app.sys import UMonitor


class BlkEventDetector(UMonitor, AsyncTask):
    def __init__(self):
        super(BlkEventDetector, self).__init__()
        self.monitor.filter_by(subsystem='block', device_type='partition')

    async def run(self):
        for device in iter(self.monitor.poll, None):
            self.info(device)
