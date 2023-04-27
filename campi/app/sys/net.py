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
from campi.topics import tNetwork


async def _net_ping(ip, port=53):
    reader, writer = await asyncio.open_connection(ip, port)


class NetEventDetector(EventDetector):
    subsystem = 'net'
    device_types = [None]

    def __init__(self, mqtt):
        super().__init__(mqtt)
        self.ping_hosts = ('8.8.8.8', '1.1.1.1')
        self.ping_trycnt = 3
        self.ping_timeout = 3
        self.ping_interval = 1
        self.ping_max_interval = 120

    async def on_ping(self):
        for _ in range(self.ping_trycnt):
            ip = random.choice(self.ping_hosts)
            try:
                task = asyncio.create_task(_net_ping(ip))
                await asyncio.wait_for(task, timeout=self.ping_timeout)
                self.mqtt.logi(f'ping interval: {self.ping_interval}')
                if self.ping_interval == 1:
                    self.mqtt.publish(tNetwork.CONNECTED, "connection")
                self.ping_interval = min(self.ping_max_interval, self.ping_interval * 2)
                return
            except ConnectionRefusedError as cerr:
                self.mqtt.logw(f'ping {ip} refused: [{cerr}]')
            except asyncio.TimeoutError as terr:
                self.mqtt.logw(f'ping {ip} timeout: [{terr}]')
                self.ping_interval = 1
        self.mqtt.publish(tNetwork.DISCONNECTED, "disconnection")

    async def handle_event(self, device):
        pass
