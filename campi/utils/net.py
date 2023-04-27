#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-23 19:30

import random
import socket
import fcntl
import struct
import subprocess


def util_get_mac(ifname='eth0'):
    # try:
    #     with open(f'/sys/class/net/{device}/address', 'r') as fr:
    #         mac = fr.readline().strip().replace(':', '')
    # except Exception:
    #     mac = "000000000000"
    # return mac
    val = '000000000000'
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        val = fcntl.ioctl(
                s.fileno(),
                0x8927,
                struct.pack('256s', bytes(ifname[:15], 'utf-8')))[18:24]
        val = ''.join(['%02x' % b for b in val])
    except Exception:
        pass
    finally:
        s.close()
    return val


def util_net_ping(hosts=('8.8.8.8', '1.1.1.1'), port=53, timeout=3):
    def_timeout = socket.getdefaulttimeout()
    val = False
    socket.setdefaulttimeout(timeout)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    for _ in range(3):
        try:
            s.connect((random.choice(hosts), port))
            val = True
            break
        except Exception:
            pass
    s.close()
    socket.setdefaulttimeout(def_timeout)
    return val


def util_wifi_connect(ssid, passwd, device='wlan0'):
    try:
        cmds = [
            'nmcli device disconnect %s 2>/dev/null' % device,
            'nmcli connection delete %s 2>/dev/null' % ssid,
            'nmcli device wifi rescan'
        ]
        subprocess.call(';'.join(cmds), shell=True)
        output = subprocess.check_output(f'nmcli device wifi connect {ssid} password {passwd}', shell=True)
        if 'successfully activated' in output.decode('utf-8').strip():
            return 0
    except subprocess.CalledProcessError as err:
        return err.returncode
    except Exception:
        pass
    return -1


MAC = util_get_mac()
