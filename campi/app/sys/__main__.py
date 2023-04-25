#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 17:23


import threading
import asyncio
from pyudev import Context, Monitor
from campi.core.atask import AsyncTask
from campi.core.amqtt import AsyncMqtt

from campi.topics import tSystem

from campi.app.sys.usb import UsbEventDetector
from campi.app.sys.blk import BlkEventDetector
from campi.app.sys.net import NetEventDetector

DEBUG = 1


class SystemEventMonitor(AsyncTask):
    def __init__(self, loop):
        self.queue = asyncio.Queue()
        self.loop = loop
        self.mqtt = AsyncMqtt('SystemEventMonitor', loop=loop)
        self.monitor = Monitor.from_netlink(Context(), source='udev')
        self.eusb = UsbEventDetector(self.mqtt).filter_by(self.monitor)
        self.eblk = BlkEventDetector(self.mqtt).filter_by(self.monitor)
        self.enet = NetEventDetector(self.mqtt).filter_by(self.monitor)

    def handle_udev_event(self):
        d = self.monitor.poll(0)
        if d is not None:
            if DEBUG:
                print(f'[{threading.current_thread().ident}]: subsystem:{d.subsystem}, device_type:{d.device_type}, action:{d.action}, device_path:{d.device_path}, device_node:{d.device_node}, sys_name:{d.sys_name}')

            async def do_task(d):
                if d.subsystem == self.eusb.subsystem:
                    await self.eusb.handle_event(d)
                elif d.subsystem == self.eblk.subsystem:
                    await self.eblk.handle_event(d)
                elif d.subsystem == self.enet.subsystem:
                    await self.enet.handle_event(d)
            asyncio.create_task(do_task(d))

    def handle_mqtt_event(self, topic, message):
        if topic == tSystem.SHUTDOWN:
            asyncio.ensure_future(self.queue.put('q'))

    async def run(self):
        if DEBUG:
            print(f'[{threading.current_thread().ident}] SystemEventMonitor async run')
        self.monitor.start()
        loop = asyncio.get_running_loop()
        loop.add_reader(self.monitor.fileno(), self.handle_udev_event)
        self.mqtt.subscribe([tSystem.SHUTDOWN], self.handle_mqtt_event)
        await self.mqtt.connect()
        self.loop.call_later(self.enet.ping_interval, self.queue.put_nowait, 'p')
        while True:
            r = await self.queue.get()
            if r == 'q':
                print("system quit")
                break
            elif r == 'p':
                await self.enet.on_ping()
                self.loop.call_later(self.enet.ping_interval, self.queue.put_nowait, 'p')


if __name__ == "__main__":
    async def system_event_monitor():
        await SystemEventMonitor(loop=asyncio.get_running_loop())
    asyncio.run(system_event_monitor())


# async def system_event_monitor():
#     monitor = Monitor.from_netlink(Context(), source='udev')
#     eusb = UsbEventDetector().filter_by(monitor)
#     eblk = BlkEventDetector().filter_by(monitor)
#     enet = NetEventDetector().filter_by(monitor)
#     # loop = asyncio.get_running_loop()
#     # loop.add_reader(monitor.fileno(), handle_udev_event, monitor)
#     monitor.start()
#     while True:
#         d = monitor.poll(enet.ping_interval)
#         if d is not None:
#             if DEBUG:
#                 import threading
#                 print(f'[{threading.current_thread().ident}]: subsystem:{d.subsystem}, device_type:{d.device_type}, action:{d.action}, device_path:{d.device_path}, device_node:{d.device_node}, sys_name:{d.sys_name}')
#             if d.subsystem == eusb.subsystem:
#                 await eusb.handle_event(d)
#             elif d.subsystem == eblk.subsystem:
#                 await eblk.handle_event(d)
#             elif d.subsystem == enet.subsystem:
#                 await enet.handle_event(d)
#         else:
#             await enet.handle_event(d)
#
# if __name__ == "__main__":
#     print('start system event monitor...')
#     asyncio.run(system_event_monitor())
