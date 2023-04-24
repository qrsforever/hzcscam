#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 17:23


import asyncio
from pyudev import Context, Monitor
# from functools import partial

from campi.app.sys.usb import UsbEventDetector
from campi.app.sys.blk import BlkEventDetector
from campi.app.sys.net import NetEventDetector

DEBUG = 1

# def handle_udev_event(monitor):
#     pass

async def system_event_monitor():
    monitor = Monitor.from_netlink(Context(), source='udev')
    eusb = UsbEventDetector().filter_by(monitor)
    eblk = BlkEventDetector().filter_by(monitor)
    enet = NetEventDetector().filter_by(monitor)
    # loop = asyncio.get_running_loop()
    # loop.add_reader(monitor.fileno(), handle_udev_event, monitor)
    monitor.start()
    while True:
        d = monitor.poll(enet.ping_interval)
        if d is not None:
            if DEBUG:
                import threading
                print(f'[{threading.current_thread().ident}]: subsystem:{d.subsystem}, device_type:{d.device_type}, action:{d.action}, device_path:{d.device_path}, device_node:{d.device_node}, sys_name:{d.sys_name}')
            if d.subsystem == eusb.subsystem:
                await eusb.handle_event(d)
            elif d.subsystem == eblk.subsystem:
                await eblk.handle_event(d)
            elif d.subsystem == enet.subsystem:
                await enet.handle_event(d)
        else:
            await enet.handle_event(d)

if __name__ == "__main__":
    print('start system event monitor...')
    asyncio.run(system_event_monitor())
