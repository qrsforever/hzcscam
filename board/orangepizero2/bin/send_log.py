#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file send_log.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-08-03 10:49

import sys
import os
import datetime

sys.path.append('/campi')

from campi.utils.oss import coss3_put

if __name__ == "__main__":
    _, log_src_file = sys.argv
    now = datetime.datetime.now()
    nd = now.strftime('%Y%m%d')
    nt = now.strftime('%H%M%S')
    cid = 'unkown'
    if os.path.exists('/sys/class/net/eth0/address'):
        with open('/sys/class/net/eth0/address', 'r') as fr:
            cid = fr.readline().strip().replace(':', '')
    filename = os.path.basename(log_src_file)
    coss3_put(log_src_file, [log_src_file, f'logs/{cid}/{nd}/{nt}_{filename}'])
