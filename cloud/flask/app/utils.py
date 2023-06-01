#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

def convert_timestamp_to_datetime(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(value))

def convert_datetime_to_timestamp(value):
    return time.mktime(time.strptime(value, '%Y-%m-%d %H:%M:%S'))
