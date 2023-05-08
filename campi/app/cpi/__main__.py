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

async def main():
    sys_h = SystemMessageHandler()  # noqa
    log_h = LoggerMessageHandler()  # noqa

    while True:
        r = await sys_h.queue.get()
        if r == 'q':
            print("system quit")
            break

if __name__ == "__main__":
    asyncio.run(main())
