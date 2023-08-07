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
from campi.topics import TNetwork


async def _dnsnet_ping(ip, port=53):
    reader, writer = await asyncio.open_connection(ip, port)

# import socket
# 
# def internet(host="8.8.8.8", port=53, timeout=3):
#     try:
#         socket.setdefaulttimeout(timeout)
#         socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
#         return True
#     except socket.error as ex:
#         print(ex)
#         return False

class NetEventDetector(EventDetector):
    subsystem = 'net'
    device_types = [None]

    def __init__(self, mqtt):
        super().__init__(mqtt)
        self.ping_hosts = (
            ('8.8.8.8', 53),
            ('8.8.4.4', 53),
            ('aiot.hzcsdata.com', 1883),
            ('www.baidu.com', 80),
            ('www.qq.com', 80)
        )
        self.ping_trycnt = 5
        self.ping_timeout = 3
        self.ping_interval = 1
        self.ping_max_interval = 120
        self.connected = False

    async def on_ping(self):
        for i in range(self.ping_trycnt):
            ip = random.choice(self.ping_hosts)
            try:
                task = asyncio.create_task(_dnsnet_ping(*ip))
                await asyncio.wait_for(task, timeout=self.ping_timeout)
                self.mqtt.logi(f'ping interval: {i} {ip}: {self.ping_interval}')
                if not self.connected:
                    self.connected = True
                    self.mqtt.publish(TNetwork.CONNECTED, "connection", qos=2)
                self.ping_interval = min(self.ping_max_interval, self.ping_interval * 2)
                return
            except ConnectionRefusedError as cerr:
                self.mqtt.logw(f'ping {ip} refused: [{cerr}]')
            except asyncio.TimeoutError as terr:
                self.mqtt.logw(f'ping {ip} timeout: [{terr}]')
            except Exception as err:
                self.mqtt.logw(f'ping {ip} error: [{err}]')
                await asyncio.sleep(self.ping_timeout)

        self.connected = False
        self.ping_interval = 1
        self.mqtt.publish(TNetwork.DISCONNECTED, "disconnection", qos=2)

    async def handle_event(self, device):
        pass
