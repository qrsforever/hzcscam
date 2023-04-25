#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 16:20


import asyncio
from campi.app.cpi.sys import SystemMessageHandler
from campi.app.cpi.log import LoggerMessageHandler

async def main_core():
    sys_h = SystemMessageHandler()  # noqa
    log_h = LoggerMessageHandler()  # noqa

    await asyncio.sleep(1000)

if __name__ == "__main__":
    asyncio.run(main_core())
