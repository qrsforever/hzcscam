#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 16:20


import sys
sys.path.append('/campi')

import asyncio
from campi.app.cpi.sys import SystemMessageHandler
from campi.app.cpi.log import LoggerMessageHandler
from campi.app.cpi.ota import OtaMessageHandler

async def main():
    sys_h = SystemMessageHandler()  # noqa
    log_h = LoggerMessageHandler()  # noqa
    ota_h = OtaMessageHandler()     # noqa

    while True:
        r = await sys_h.queue.get()
        if r == 'q':
            print("system quit")
            break

    import os
    os.system("reboot")

if __name__ == "__main__":
    asyncio.run(main())
