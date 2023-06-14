#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-08 23:12


import subprocess
import requests
import json
import os

from . import MessageHandler
from campi.constants import (
    ARCHIVES_ROOT_PATH,
    RUNTIME_PATH,
    VERSION_APP_PATH,
)
from campi.topics import TCloud
from campi.topics import TUpgrade


def compare_version(vnew, vold):
    if vnew == vold:
        return False
    new = vnew.split('.')
    old = vold.split('.')
    for i in range(min(len(new), len(old))):
        if int(new[i]) > int(old[i]):
            return True
    return False


class OtaMessageHandler(MessageHandler):
    UPGRADE_NOOP = 0
    UPGRADE_SUCESS = 1
    UPGRADE_FAIL = -1

    UPGRADE_METHOD_DISK = 1
    UPGRADE_METHOD_HTTP = 2

    def __init__(self):
        super().__init__([TCloud.OTA, TUpgrade.BY_UDISK, TUpgrade.BY_OTA])
        with open(VERSION_APP_PATH, 'r') as fr:
            self.app_version = fr.read().strip()

        self.conn_timeout = 3
        self.read_timeout = 3

    def _do_upgrade(self, config):
        self.logger.info("upgrade ...")

        zip_md5 = config['md5']
        zip_path = config['zip_path']
        compatible = config.get('compatible', True)
        execsetup = config.get('execsetup', True)
        appversion = config.get('version', '1.0.0')
        try:
            md5 = subprocess.check_output(f'md5sum {zip_path} | cut -c1-32', shell=True)
            if md5.decode('utf-8').strip() != zip_md5:
                config['reason'] = 'md5 not match'
                return self.UPGRADE_FAIL
            subprocess.call(f'unzip -qo {zip_path} -d {ARCHIVES_ROOT_PATH}/{appversion}', shell=True)
            if compatible:
                subprocess.call(f'cp -aprf {RUNTIME_PATH} {ARCHIVES_ROOT_PATH}/{appversion}/', shell=True)
            if execsetup:
                subprocess.call(f'{ARCHIVES_ROOT_PATH}/{appversion}/scripts/setup_service.sh', shell=True)
            subprocess.call('rm -rf $(readlink /campi)', shell=True)
            subprocess.call(f'rm -f /campi; ln -s {ARCHIVES_ROOT_PATH}/{appversion} /campi', shell=True)
            return self.UPGRADE_SUCESS
        except Exception as err:
            config['reason'] = f'subprocess upgrade fail {err}'
            return self.UPGRADE_FAIL

    def handle_message(self, topic, message):
        self.logger.info(f'ota {topic} {message}')

        if topic in (TUpgrade.BY_UDISK, TCloud.OTA):
            config = json.loads(message) if isinstance(message, str) else message

            force = config.get('force', False)
            if not force and not compare_version(config['version'], self.app_version):
                self.logger.info(f"save version: {config['version']}, {self.app_version}")
                return

            if topic == TCloud.OTA:
                zip_res = requests.get(
                    config['url'],
                    headers={'Content-Type': 'application/zip'},
                    timeout=(self.conn_timeout, self.read_timeout))
                if zip_res.status_code != 200:
                    self.send_message(TCloud.UPGRADE_FAIL, config)
                with open('/tmp/campi_update.zip', 'wb') as fw:
                    fw.write(zip_res.content)
                config['zip_path'] = '/tmp/campi_update.zip'

            if self.UPGRADE_SUCESS == self._do_upgrade(config):
                self.logger.info("upgrade success")
                self.send_message(TCloud.UPGRADE_SUCESS, config)
                os.system("sleep 3; reboot")
            else:
                self.logger.error(f"upgrade fail {config}")
                self.send_message(TCloud.UPGRADE_FAIL, config)
            return
