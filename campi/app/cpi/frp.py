#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file frp.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-16 12:16


import json
from . import MessageHandler
from campi.topics import TCloud
from campi.constants import FRP_CONFIG_PATH

from campi.utils.shell import util_start_service, util_stop_service

FRPC_TEMPLATE_INI = """
[common]
server_addr = %s
server_port = %d

[ssh]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = %d
"""


class FrpcMessageHandler(MessageHandler):

    SNAME = 'campi_frp.service'

    def __init__(self):
        super().__init__([TCloud.FRPC_CTRL])

    def _set_frpc(self, config):
        enable = config.get('frpc_enable', False)
        if not enable:
            util_stop_service(self.SNAME)
            return

        server_addr = config.get('server_addr', None)
        server_port = config.get('server_port', 7777)
        remote_port = config.get('remote_port', None)

        if server_addr is None or remote_port is None:
            return

        with open(FRP_CONFIG_PATH, 'w') as fw:
            fw.write(FRPC_TEMPLATE_INI % (server_addr, server_port, remote_port))
        util_start_service(self.SNAME, True)

    def handle_message(self, topic, message):
        self.logger.debug(f'frpc: {message}')

        jdata = json.loads(message)
        if topic == TCloud.FRPC_CTRL:
            return self._set_frpc(jdata)