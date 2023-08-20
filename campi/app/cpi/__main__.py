#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 16:20


import sys
import os
sys.path.append('/campi')

if os.path.exists('/sys/class/net/eth0/address'):
    with open('/sys/class/net/eth0/address', 'r') as fr:
        os.environ['ADDRESS'] = fr.readline().strip().replace(':', '')

if os.path.exists('/campi/version.txt'):
    with open('/campi/version.txt', 'r') as fr:
        os.environ['APP_VERSION'] = fr.read().strip()

import asyncio
from campi.app.cpi.sys import SysMessageHandler
from campi.app.cpi.log import LogMessageHandler
from campi.app.cpi.ota import OtaMessageHandler
from campi.app.cpi.gst import GstMessageHandler
from campi.app.cpi.emq import EmqMessageHandler
from campi.app.cpi.frp import FrpMessageHandler

from campi.utils.shell import util_start_service

heartbeat_interval = 300

async def main():
    sys_h = SysMessageHandler()  # noqa
    log_h = LogMessageHandler()  # noqa
    ota_h = OtaMessageHandler()  # noqa
    gst_h = GstMessageHandler()  # noqa
    emq_h = EmqMessageHandler()  # noqa
    frp_h = FrpMessageHandler()  # noqa

    loop = asyncio.get_running_loop()
    loop.call_later(5, sys_h.queue.put_nowait, 'h')
    report_more = False
    while True:
        r = await sys_h.queue.get()
        if r == 'q':
            print("system quit")
            break
        elif r == 'h':
            if not report_more:
                await sys_h.do_heartbeat(True)
                report_more = True
            else:
                await sys_h.do_heartbeat(False)
            loop.call_later(heartbeat_interval, sys_h.queue.put_nowait, 'h')

    await asyncio.sleep(3)
    # TODO orangepizero2 reboot will fail, cannot startup.
    # os.system("reboot -f")
    util_start_service('campi_boot.service')

if __name__ == "__main__":
    asyncio.run(main())
