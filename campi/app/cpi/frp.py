#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file frp.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-16 12:16


import json
import os
from . import MessageHandler
from campi.topics import TCloud
from campi.constants import FRP_CONFIG_PATH, SVC_FRP

from campi.utils.shell import util_start_service, util_stop_service

FRPC_TEMPLATE_INI = """
[common]
server_addr = %s
server_port = %d

[ssh%d]
type = tcp
local_ip = 127.0.0.1
local_port = 22
remote_port = %d
"""


class FrpMessageHandler(MessageHandler):

    SNAME = SVC_FRP

    def __init__(self):
        super().__init__([TCloud.FRPC_CLOUD_CTRL])

        self.config = self._read_config()
        if self.config.get('frpc_enable'):
            util_start_service(self.SNAME)

    def _set_frpc(self, config):
        enable = config.get('frpc_enable', False)
        if not enable:
            self.config = {'frpc_enable': False}
            util_stop_service(self.SNAME)
            os.remove(FRP_CONFIG_PATH)
            return

        server_addr = config.get('server_addr', None)
        server_port = config.get('server_port', 7777)
        remote_port = config.get('remote_port', None)

        if server_addr is None or remote_port is None:
            return
        self.config = config
        with open(FRP_CONFIG_PATH, 'w') as fw:
            fw.write(FRPC_TEMPLATE_INI % (server_addr, server_port, remote_port, remote_port))
        util_start_service(self.SNAME, False)

    def _read_config(self):
        config = {'frpc_enable': False}
        if os.path.exists(FRP_CONFIG_PATH):
            config['frpc_enable'] = True
            with open(FRP_CONFIG_PATH, 'r') as fr:
                for line in fr.readlines():
                    if 'server_addr' in line:
                        config['server_addr'] = line.split('=')[1].strip()
                    elif 'server_port' in line:
                        config['server_port'] = int(line.split('=')[1].strip())
                    elif 'remote_port' in line:
                        config['remote_port'] = int(line.split('=')[1].strip())
        return config

    def get_info(self):
        return {'frp': self.config}

    def handle_message(self, topic, message):
        self.logger.debug(f'frpc: {message}')

        jdata = json.loads(message)
        if topic == TCloud.FRPC_CLOUD_CTRL:
            return self._set_frpc(jdata)
