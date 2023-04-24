#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file blk.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 18:14


import os
import subprocess
from . import EventDetector
from campi.topics import tUsbDisk


class BlkEventDetector(EventDetector):
    subsystem = 'block'
    device_types = ['partition']

    def __init__(self, mqtt):
        super().__init__(mqtt)

    def on_mount(self, devnode, mntdir):
        if not os.path.isdir(mntdir):
            os.mkdir(mntdir)
        try:
            subprocess.call(f'mount {devnode} {mntdir}', shell=True)
            if os.path.ismount(mntdir):
                print('mount ok')
                self.mqtt.publish(tUsbDisk.MOUNTED, "test")
        except Exception:
            pass

    def on_umount(self, devnode, mntdir):  # pyright:ignore
        if os.path.ismount(mntdir):
            subprocess.call(f'umount -l {mntdir}', shell=True)
            print('umount ok')
            self.mqtt.publish(tUsbDisk.UMOUNTED, "test")

    async def handle_event(self, device):
        if device.device_type == 'partition':
            if not device.device_node.startswith('/dev/sd'):
                return
            if device.action == 'add':
                return self.on_mount(device.device_node, f'/mnt/{device.sys_name}')
            elif device.action == 'remove':
                return self.on_umount(device.device_node, f'/mnt/{device.sys_name}')
