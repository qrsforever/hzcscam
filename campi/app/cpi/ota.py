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
import shutil

from . import MessageHandler
from campi.constants import (
    ARCHIVES_ROOT_PATH,
    RUNTIME_PATH,
    APP_VERSION,
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
        super().__init__([TCloud.OTA, TUpgrade.BY_UDISK, TUpgrade.BY_OTA, TUpgrade.BY_AUTO])

        self.conn_timeout = 3
        self.read_timeout = 3
        self.upgrade_server = 'http://aiot.hzcsdata.com:30082/version_info.json'
        self.zip_path = f'{ARCHIVES_ROOT_PATH}/update.zip'

    def _do_upgrade(self, config):
        self.logger.info("upgrade ...")

        zip_md5 = config['md5']
        compatible = config.get('compatible', True)
        execsetup = config.get('execsetup', True)
        try:
            if os.path.isdir(f'{ARCHIVES_ROOT_PATH}/{zip_md5}'):
                config['reason'] = 'md5 already exist.'
                return self.UPGRADE_FAIL
            md5 = subprocess.check_output(f'md5sum {self.zip_path} | cut -c1-32', shell=True)
            md5 = md5.decode('utf-8').strip()
            if md5 != zip_md5:
                self.logger.error(f'md5: {md5} vs {zip_md5}')
                config['reason'] = 'md5 not match'
                return self.UPGRADE_FAIL
            subprocess.call(f'unzip -qo {self.zip_path} -d {ARCHIVES_ROOT_PATH}/{zip_md5}', shell=True)
            if os.path.isdir(f'{ARCHIVES_ROOT_PATH}/{zip_md5}'):
                if compatible:
                    subprocess.call(f'cp -aprf {RUNTIME_PATH} {ARCHIVES_ROOT_PATH}/{zip_md5}', shell=True)
                if execsetup:
                    subprocess.call(f'{ARCHIVES_ROOT_PATH}/{zip_md5}/scripts/setup_service.sh', shell=True)
                subprocess.call('rm -rf $(readlink /campi)', shell=True)
                subprocess.call(f'rm -f /campi; ln -s {ARCHIVES_ROOT_PATH}/{zip_md5} /campi', shell=True)
                return self.UPGRADE_SUCESS
            config['reason'] = 'unzip fail!'
            return self.UPGRADE_FAIL
        except Exception as err:
            config['reason'] = f'subprocess upgrade fail {err}'
            return self.UPGRADE_FAIL

    def _on_check_upgrade(self, config):
        force = config.get('force', False)
        if not force and not compare_version(config['version'], APP_VERSION):
            self.logger.info(f"save version: {config['version']}, {APP_VERSION}")
            return False
        return True

    def _on_request_upgrade_config(self):
        config_res = requests.get(
            self.upgrade_server,
            headers={'Content-Type': 'application/json'},
            timeout=(self.conn_timeout, self.read_timeout))
        if config_res.status_code != 200:
            self.logger.error(f"upgrade request config: requests error[{config_res.status_code}]!")
            self.send_message(TCloud.UPGRADE_REQUEST_ERROR, "{}")
            return None
        return json.loads(config_res.content)

    def _on_request_upgrade_zip(self, config):
        zip_res = requests.get(
            config['url'],
            headers={'Content-Type': 'application/zip'},
            timeout=(self.conn_timeout, self.read_timeout))
        if zip_res.status_code != 200:
            self.logger.error(f"upgrade fail: requests error[{zip_res.status_code}]!")
            self.send_message(TCloud.UPGRADE_FAIL, config)
            return False
        if os.path.exists(self.zip_path):
            shutil.move(self.zip_path, f'{ARCHIVES_ROOT_PATH}/factory.zip')
        with open(self.zip_path, 'wb') as fw:
            fw.write(zip_res.content)
        return True

    def handle_message(self, topic, message):
        self.logger.info(f'ota: {topic} {message}')

        if topic in (TUpgrade.BY_UDISK, TCloud.OTA, TUpgrade.BY_AUTO):
            if topic == TUpgrade.BY_AUTO:
                config = self._on_request_upgrade_config()
            else:
                config = json.loads(message) if isinstance(message, str) else message
            if not self._on_check_upgrade(config):
                return

            if topic == TCloud.OTA or topic == TUpgrade.BY_AUTO:
                if not self._on_request_upgrade_zip(config):
                    return

            if self.UPGRADE_SUCESS == self._do_upgrade(config):
                self.logger.info("upgrade success")
                self.send_message(TCloud.UPGRADE_SUCESS, config)
                self.quit()
            else:
                self.logger.error(f"upgrade fail {config}")
                self.send_message(TCloud.UPGRADE_FAIL, config)
            return
