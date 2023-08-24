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

# from campi.utils.shell import util_get_uptime
from campi.constants import (
    # SCRIPT_OF_START_AP, SCRIPT_OF_STOP_AP,
    SCRIPT_OF_SET_WIFI,
    VERSION_OTA_FILE, WIFI_NM_CONF, WIFI_NM_FILE)

from campi.utils.net import (
    util_net_ping, util_get_mac, util_get_lanip,
    util_get_netip, util_get_gateway, util_get_subnet,
    util_get_wifi_sigth, util_get_wifi_transrate, util_send_mail)

# from campi.utils.shell import (
#     util_start_service,
#     util_stop_service)

WIFIAP_TIMEOUT = 250
WIFIAP_NOSTATE = 0
WIFIAP_RUNNING = 1
WIFIAP_STOPING = 2

NET_STATE_UNINITED = 0
NET_STATE_CONNECTED = 1
NET_STATE_DISCONNECTED = 2

MAX_TIMER_BUFLEN = 5

class SysMessageHandler(MessageHandler):

    def __init__(self):
        super().__init__([
            TNetwork.ALL,
            TUsbDisk.ALL,
            TSystem.SHUTDOWN,
            TApis.SET_WIFI,
            TCloud.NETWORK_SET_WIFI,
            TCloud.SYS_REBOOT,
            TCloud.EVENTS_REPORT,
            TCloud.EVENTS_CLOUD_REPORT,
        ])
        self.wifiap_state = WIFIAP_NOSTATE
        self.network_state = NET_STATE_UNINITED
        if util_net_ping():
            self.on_network_connected('')
        else:
            self.on_network_disconnect('')

        self.conn_times = [0] * MAX_TIMER_BUFLEN
        self.curr_index = 0

    def on_network_connected(self, message):# {{{
        self.logger.info('network connect: %s' % message)
        self.conn_time = [int(message)] * MAX_TIMER_BUFLEN
        if self.network_state != NET_STATE_CONNECTED:
            util_send_mail(json.dumps({
                'mac': util_get_mac(),
                'lanip': util_get_lanip(),
                'netip': util_get_netip()
            }))
            self.network_state = NET_STATE_CONNECTED
# }}}

    def on_network_disconnect(self, message):# {{{
        self.logger.warn('network disconnect')
        if self.network_state != NET_STATE_DISCONNECTED:
            self.network_connected = NET_STATE_DISCONNECTED

        # def _start_wifiap():
        #     self.logger.error(f'start wifiap: {self.wifiap_state}')
        #     try:
        #         process = subprocess.Popen(
        #                 SCRIPT_OF_START_AP,
        #                 stdout=subprocess.PIPE,
        #                 stderr=subprocess.PIPE,
        #                 shell=True)
        #         for line in process.stdout:
        #             self.logger.info(line.decode("utf-8").strip())
        #     except subprocess.CalledProcessError as cerr:
        #         self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {cerr}')
        #     except Exception as oerr:
        #         self.logger.error(f'start ap err[{SCRIPT_OF_START_AP}]: {oerr}')

        # if util_get_uptime() < WIFIAP_TIMEOUT:
        #     if self.wifiap_state == WIFIAP_NOSTATE:
        #         multiprocessing.Process(target=_start_wifiap).start()
        #         self.wifiap_state = WIFIAP_RUNNING
        # else:
        #     if os.path.exists(WIFI_NM_CONF):
        #         with open(WIFI_NM_CONF, 'r') as fr:
        #             self.on_network_setwifi(fr.read())
# }}}

    def on_network_setwifi(self, message):# {{{
        jdata = json.loads(message)

        def _set_wifi():
            self.logger.info('set wifi...')
            # if self.wifiap_state != WIFIAP_STOPING:
            #     try:
            #         process = subprocess.Popen(
            #                 SCRIPT_OF_STOP_AP,
            #                 stdout=subprocess.PIPE,
            #                 stderr=subprocess.PIPE,
            #                 shell=True)
            #         for line in process.stdout:
            #             self.logger.info(line.decode("utf-8").strip())
            #         self.wifiap_state = WIFIAP_STOPING
            #     except subprocess.CalledProcessError as cerr:
            #         self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {cerr}')
            #     except Exception as oerr:
            #         self.logger.error(f'start ap err[{SCRIPT_OF_STOP_AP}]: {oerr}')

            try:
                ssid = jdata.get("wifissid", "hzcsdata")
                pswd = jdata.get("password", "Hzcsai@123")
                bsid = jdata.get("expbssid", "")
                process = subprocess.Popen(
                        f'{SCRIPT_OF_SET_WIFI} {ssid} {pswd} {bsid}',
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        shell=True)
                for line in process.stdout:
                    line = line.decode("utf-8").strip()
                    self.logger.info(line)
                    if 'success' in line:
                        with open(WIFI_NM_CONF, 'w') as fw:
                            json.dump(jdata, fw)
                        self.quit()
            except subprocess.CalledProcessError as cerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {cerr}')
            except Exception as oerr:
                self.logger.error(f'set wifi err[{SCRIPT_OF_SET_WIFI}]: {oerr}')

        multiprocessing.Process(target=_set_wifi).start()
# }}}

    def on_network_heartbeat(self, message):# {{{
        self.logger.warn('network heartbeat: %s' % message)
        self.curr_index = (self.curr_index + 1) % MAX_TIMER_BUFLEN
        self.conn_times[self.curr_index] = int(message)
        self.send_message(TCloud.EVENTS_HEARTBEAT, {
            'ping_time_ms': sum(self.conn_times) / MAX_TIMER_BUFLEN
        })
# }}}

    def on_udisk_mounted(self, mntdir):# {{{
        wifinm_path = f'{mntdir}/campi/{WIFI_NM_FILE}'
        if os.path.isfile(wifinm_path):
            self.logger.info(f'{wifinm_path} found!')
            shutil.copyfile(wifinm_path, WIFI_NM_CONF)
            with open(WIFI_NM_CONF, 'r') as fr:
                self.on_network_setwifi(fr.read())

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
# }}}

    def handle_message(self, topic, message):
        self.logger.info(f'{topic} {message}')

        if topic == TNetwork.DISCONNECTED:
            return self.on_network_disconnect(message)

        if topic == TNetwork.CONNECTED:
            return self.on_network_connected(message)

        if topic == TNetwork.HEARTBEAT:
            return self.on_network_heartbeat(message)

        if topic == TCloud.NETWORK_SET_WIFI or topic == TApis.SET_WIFI:
            return self.on_network_setwifi(message)

        if topic == TUsbDisk.MOUNTED:
            return self.on_udisk_mounted(message)

        if topic == TCloud.EVENTS_CLOUD_REPORT or topic == TCloud.EVENTS_REPORT:
            return self.do_report(message)

        if topic == TSystem.SHUTDOWN or TCloud.SYS_REBOOT:
            self.quit()

    def get_info(self):
        return {
            'sys': {
                'ip': util_get_lanip(),
                'mac': C.ADDRESS,
                'subnet': util_get_subnet(),
                'gateway': util_get_gateway(),
                'signal_strength': util_get_wifi_sigth(),
                'transfer_rate': util_get_wifi_transrate(),
                'software_version': C.APP_VERSION,
                'hardware_product': C.BOARD,
            }
        }

    def do_report(self, message):
        jdata = json.loads(message)
        all_flag = True if len(jdata) == 0 else False
        report = {}
        for h in self.handlers:
            for key, value in h.get_info().items():
                if all_flag or (key in jdata and jdata[key]):
                    report[key] = value
        self.send_message(TCloud.EVENTS_CAMPI_REPORT, report)

    async def do_heartbeat(self, more=False):
        self.logger.info('do heartbeat')
        about = {
            'disk_usage_percent': psutil.disk_usage('/').percent,
            'cpu_percent': psutil.cpu_percent(),
            'cpu_memory_percent': psutil.virtual_memory().percent
        }
        self.send_message(TCloud.EVENTS_HEARTBEAT, about)
        if more:
            for h in self.handlers:
                for key, value in h.get_info().items():
                    about[key] = value
            self.send_message(TCloud.EVENTS_ABOUT, about)
