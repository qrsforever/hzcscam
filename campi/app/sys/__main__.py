#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 17:23

import asyncio

from campi.app.sys.usb import UsbEventDetector
from campi.app.sys.blk import BlkEventDetector
from campi.app.sys.net import NetEventDetector


async def sys_main():
    blk = BlkEventDetector()
    net = NetEventDetector()
    # usb = UsbEventDetector()
    await asyncio.gather(blk, net)


if __name__ == "__main__":
    asyncio.run(sys_main())
