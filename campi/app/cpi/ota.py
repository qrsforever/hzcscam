#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file ota.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-08 23:12


import subprocess

from . import MessageHandler
from campi.constants import (
    ARCHIVES_ROOT_PATH,
    ARCHIVES_CURRENT_PATH,
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

    def __init__(self):
        super().__init__([TCloud.OTA, TUpgrade.BY_UDISK, TUpgrade.OTA])
        with open(VERSION_APP_PATH, 'r') as fr:
            self.app_version = fr.read().strip()

    def _unzip_tarball(self, zip_path, dst_path, compatible):
        try:
            subprocess.check_call(f'unzip -qo {zip_path} -d {dst_path}', shell=True)
            if compatible:
                subprocess.check_call(f'cp -aprf {RUNTIME_PATH} {dst_path}/', shell=True)
            subprocess.check_call(f'cp -aprf {RUNTIME_PATH} {dst_path}/', shell=True)

            return 0
        except subprocess.CalledProcessError as err:
            return err.returncode
        except Exception:
            pass
        return -1

    def _do_upgrade(self, zip_url, config):
        force = config.get('force', False)
        if not force and compare_version(config['version'], self.app_version):
            return self.UPGRADE_NOOP

        if config['method'] == 'http':
            pass

        zip_md5 = config['md5']
        zip_path = config['zip_path']
        md5 = subprocess.check_output(f'md5sum {zip_path} | cut -c1-32', shell=True)
        if md5.decode('utf-8').strip() != zip_md5:
            config['reason'] = 'md5 not match'
            return self.UPGRADE_FAIL
        if self._unzip_tarball(zip_path, ARCHIVES_ROOT_PATH, config.get('compatible', True)) != 0:
            config['reason'] = 'unzip tarball fail'
            return self.UPGRADE_FAIL
        
            

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == TUpgrade.BY_UDISK:
            message['method'] = 'disk'
            # if self._unzip_tarball(message['zip_url']) == 0:
            #     self.to_cloud(TUpgrade.BY_UDISK, message)
            return

        if topic == TCloud.OTA:
            message['method'] = 'http'
            return
