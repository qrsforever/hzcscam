#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file net.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-23 19:30

import random
import socket


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
