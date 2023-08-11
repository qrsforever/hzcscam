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
    OTA_UPGRADE_CONF,
    APP_VERSION,
    SCOLOR,
)
from campi.topics import TCloud
from campi.topics import TUpgrade
from campi.topics import TSensor


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
        super().__init__([
            TCloud.OTA_AUTO, TCloud.OTA_UPGRADE, TCloud.OTA_CONFIG,
            TUpgrade.BY_UDISK, TUpgrade.BY_OTA, TUpgrade.BY_AUTO])

        self.ota_config = self._load_config()
        self.conn_timeout = 3
        self.read_timeout = 3
        self.zip_path = f'{ARCHIVES_ROOT_PATH}/update.zip'

    def _load_config(self):
        if os.path.exists(OTA_UPGRADE_CONF):
            with open(OTA_UPGRADE_CONF, 'r') as fr:
                return json.load(fr)
        else:
            return {"upgrade_server": "http://aiot.hzcsdata.com:30082"}

    def _save_config(self, config):
        self.ota_config = config
        with open(OTA_UPGRADE_CONF, 'w') as fw:
            json.dump(config, fw)
        return

    def get_info(self):# {{{
        config = {
            "ota": self.ota_config
        }
        self.logger.info(f'ota config: {config}')
        return config
# }}}

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
            self.logger.info("upgrade ma5 ok ...")
            subprocess.call(f'unzip -qo {self.zip_path} -d {ARCHIVES_ROOT_PATH}/{zip_md5}', shell=True)
            if os.path.isdir(f'{ARCHIVES_ROOT_PATH}/{zip_md5}'):
                self.logger.info("upgrade unzip ok ...")
                if compatible:
                    subprocess.call(f'cp -aprf {RUNTIME_PATH} {ARCHIVES_ROOT_PATH}/{zip_md5}', shell=True)
                if execsetup:
                    subprocess.call(f'{ARCHIVES_ROOT_PATH}/{zip_md5}/scripts/setup_service.sh', shell=True)
                subprocess.call('rm -rf $(readlink /campi)', shell=True)
                subprocess.call(f'rm -f /campi; ln -s {ARCHIVES_ROOT_PATH}/{zip_md5} /campi', shell=True)
                self.logger.info("upgrade setup ok ...")
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
            self.ota_config['upgrade_server'] + '/version_info.json',
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

        if topic == TCloud.OTA_CONFIG:
            return self._save_config(json.loads(message))

        self.logger.info("upgrade start...")
        self.send_message(TCloud.UPGRADE_START, {'from': topic})
        self.send_message(TSensor.COLOR_BLINK, {'color': SCOLOR.RED, 'count': 8, 'interval': 200})

        if topic == TCloud.OTA_UPGRADE or topic == TUpgrade.BY_UDISK:
            config = json.loads(message) if isinstance(message, str) else message
        else:
            config = self._on_request_upgrade_config()

        if not self._on_check_upgrade(config):
            return

        if topic == TUpgrade.BY_UDISK:
            shutil.copyfile(config['zip_path'], self.zip_path)
        else:
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
