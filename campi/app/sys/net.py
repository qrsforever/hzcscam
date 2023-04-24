#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 22:53

import asyncio
import random
from . import EventDetector


async def _net_ping(ip, port=53):
    reader, writer = await asyncio.open_connection(ip, port)  # pyright:ignore


class NetEventDetector(EventDetector):
    subsystem = 'net'
    device_types = [None]

    def __init__(self):
        self.ping_hosts = ('8.8.8.8', '1.1.1.1')
        self.ping_trycnt = 3
        self.ping_timeout = 3
        self.ping_interval = 1
        self.ping_max_interval = 56

    async def on_ping(self):
        for _ in range(self.ping_trycnt):
            ip = random.choice(self.ping_hosts)
            try:
                task = asyncio.create_task(_net_ping(ip))
                await asyncio.wait_for(task, timeout=self.ping_timeout)
                print(self.ping_interval)
                self.ping_interval = min(self.ping_max_interval, self.ping_interval * 2)
                break
            except asyncio.TimeoutError:
                self.ping_interval = 1

    async def handle_event(self, device):
        if device is None:
            return await self.on_ping()
