#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file sys.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-25 17:31


import multiprocessing
import subprocess
import json
import os
import psutil
import shutil

from . import MessageHandler
from campi.topics import (
    TNetwork,
    TUsbDisk,
    TCloud,
    TSystem,
    TUpgrade,
    TApis)

import campi.constants as C
from campi.constants import (
    SCRIPT_OF_SET_WIFI, SCRIPT_OF_START_AP, SCRIPT_OF_STOP_AP,
    VERSION_OTA_FILE, WIFI_NM_CONF, WIFI_NM_FILE)

from campi.utils.net import (
    util_net_ping,
    util_get_mac,
    util_get_lanip,
    util_get_netip,
    util_send_mail)

from campi.utils.shell import util_get_uptime


WIFIAP_TIMEOUT = 250
WIFIAP_NOSTATE = 0
WIFIAP_RUNNING = 1
WIFIAP_STOPING = 2


class SystemMessageHandler(MessageHandler):

    def __init__(self):
        super().__init__([
            TNetwork.ALL,
            TUsbDisk.ALL,
            TSystem.SHUTDOWN,
            TApis.SET_WIFI,
            TCloud.EVENTS_CLOUD_REPORT,
        ])
        self.heartbeat_interval = 300
        self.wifiap_state = WIFIAP_NOSTATE
        self.network_connected = util_net_ping()
        self.wifi_ssid_pswd = None

    def on_network_connected(self, message):# {{{
        # TODO
        self.network_connected = True

        util_send_mail(json.dumps({
            'mac': util_get_mac(),
            'lanip': util_get_lanip(),
            'netip': util_get_netip()
        }))
# }}}

    def on_network_disconnect(self, message):# {{{
        self.network_connected = False
        # TODO
        return

        def _start_wifiap():
            self.logger.error(f'start wifiap: {self.wifiap_state}')
            try:
                process = subprocess.Popen(
                        SCRIPT_OF_START_AP,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    self.logger.info(line.decode("utf-8").strip())
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {oerr}')

        if util_get_uptime() < WIFIAP_TIMEOUT:
            if self.wifiap_state == WIFIAP_NOSTATE:
                multiprocessing.Process(target=_start_wifiap).start()
                self.wifiap_state = WIFIAP_RUNNING
        else:
            if os.path.exists(WIFI_NM_CONF):
                with open(WIFI_NM_CONF, 'r') as fr:
                    self.on_network_setwifi(fr.read())
# }}}

    def on_network_setwifi(self, message):# {{{
        jdata = json.loads(message)

        def _set_wifi():
            self.logger.error(f'set wfif, wifiap state: {self.wifiap_state}')
            if self.wifiap_state != WIFIAP_STOPING:
                try:
                    process = subprocess.Popen(
                            SCRIPT_OF_STOP_AP,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=True)
                    for line in process.stdout:
                        self.logger.info(line.decode("utf-8").strip())
                    self.wifiap_state = WIFIAP_STOPING
                except subprocess.CalledProcessError as cerr:
                    self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {cerr}')
                except Exception as oerr:
                    self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {oerr}')

            try:
                process = subprocess.Popen(
                        f'{SCRIPT_OF_SET_WIFI} {jdata["wifissid"]} {jdata["password"]}',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    line = line.decode("utf-8").strip()
                    self.logger.info(line)
                    if 'success' in line:
                        with open(WIFI_NM_CONF, 'w') as fw:
                            json.dump(jdata, fw)
                        self.wifi_ssid_pswd = jdata
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {oerr}')

        multiprocessing.Process(target=_set_wifi).start()
# }}}

    def on_udisk_mounted(self, mntdir):# {{{
        verinfo_path = f'{mntdir}/campi/{VERSION_OTA_FILE}'
        if os.path.isfile(verinfo_path):
            self.logger.info(f'{verinfo_path} found!')
            with open(verinfo_path, 'r') as fr:
                version_info = json.load(fr)
                zip_path = f'{mntdir}/campi/{version_info["url"]}'
                if os.path.isfile(zip_path):
                    version_info['zip_path'] = zip_path
                    self.send_message(TUpgrade.BY_UDISK, json.dumps(version_info))
            return

        wifinm_path = f'{mntdir}/campi/{WIFI_NM_FILE}'
        if os.path.isfile(wifinm_path):
            shutil.copyfile(wifinm_path, WIFI_NM_CONF)
            self.quit()
# }}}

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == TNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)

        if topic == TNetwork.CONNECTED:
            return self.on_network_connected(message)

        if topic == TApis.SET_WIFI:
            return self.on_network_setwifi(message)

        if topic == TUsbDisk.MOUNTED:
            return self.on_udisk_mounted(message)

        if topic == TCloud.EVENTS_CLOUD_REPORT:
            return self.do_report(message)

        if topic == TSystem.SHUTDOWN:
            self.quit()

    def get_info(self):
        return {
            'sys': {
                'ip': util_get_lanip(),
                'mac': C.ADDRESS,
                'software_version': C.APP_VERSION,
                'hardware_product': C.BOARD,
            }
        }

    def do_report(self, message):
        jdata = json.loads(message)
        report = {}
        for h in self.handlers:
            for key, value in h.get_info().items():
                if key in jdata and jdata[key]:
                    report[key] = value
        self.send_message(TCloud.EVENTS_CAMPI_REPORT, report)

    async def do_heartbeat(self, more=False):
        if not self.network_connected:
            self.logger.warn("network is not connected, heartbeat fail")
            return
        about = {
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'cpu_percent': psutil.cpu_percent(),
            'cpu_memory_percent': psutil.virtual_memory().percent
        }
        if more:
            for key, value in self.get_info().items():
                about[key] = value
            self.send_message(TCloud.EVENTS_ABOUT, about)
        else:
            self.send_message(TCloud.EVENTS_HEARTBEAT, about)
