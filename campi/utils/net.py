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
import os


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


def util_get_lanip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]
    except Exception:
        pass
    finally:
        s.close()
    return ''

def util_get_netip():
    result = os.popen('curl -s http://txt.go.sohu.com/ip/soip | grep -P -o -i "(\d+\.\d+.\d+.\d+)"', 'r') # noqa
    if result:
        return result.read().strip('\n')
    return ''

def util_get_subnet():
    ip = util_get_lanip()
    if len(ip) == 0:
        return ''
    result = os.popen("ip route | grep 'src " + ip + "' | awk '{print $1}'", 'r')
    if result:
        return result.read().strip('\n')
    return ''

def util_get_gateway():
    result = os.popen("ip route show | grep default | awk '{print $3}'", 'r')
    if result:
        return result.read().strip('\n')
    return ''

def util_get_wifi_sigth():
    result = os.popen("nmcli dev wifi list | awk '/\*/{if (NR!=1) {print $8}}'", 'r')
    if result:
        return int(result.read().strip('\n'))
    return 0

def util_wifi_connect(ssid, passwd, device='wlan0'):
    try:
        cmds = [
            'nmcli device disconnect %s 2>/dev/null' % device,
            'nmcli connection delete %s 2>/dev/null' % ssid,
            'nmcli device wifi rescan', 'sleep 5'
        ]
        subprocess.call(';'.join(cmds), shell=True)
        output = subprocess.check_output(f'nmcli device wifi connect {ssid} password {passwd}', shell=True)
        if 'successfully activated' in output.decode('utf-8').strip():
            return 0
    except subprocess.CalledProcessError as perr:
        print(perr)
        return perr.returncode
    except Exception as err:
        print(err)
    return -1


MAC = util_get_mac()


def util_send_mail(msg):
    import smtplib
    from email.mime.text import MIMEText

    EMAIL_SENDER = 'erlangai@qq.com'
    EMAIL_PASSWD = 'napynuczfljubffa'
    EMAIL_RECVER = 'erlang47@qq.com'

    text = MIMEText(msg, 'plain', 'utf-8')
    text['From'] = EMAIL_SENDER
    text['To'] = EMAIL_RECVER
    text['Subject'] = 'orangepi'

    try:
        smtp = smtplib.SMTP('smtp.qq.com')
        smtp.login(EMAIL_SENDER, EMAIL_PASSWD)
        smtp.send_message(text)
        smtp.quit()
    except smtplib.SMTPException as e:
        print(e)
    except Exception as e:
        print(e)
