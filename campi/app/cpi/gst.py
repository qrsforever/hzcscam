#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gst.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-15 15:01

import json

from . import MessageHandler
from campi.constants import (
    ADDRESS,
    GST_CONFIG_PATH,
)

from campi.utils.shell import (
    util_check_service,
    util_start_service,
    util_stop_service,
)

from campi.topics import TCloud as T


class GstMessageHandler(MessageHandler):

    SNAME = 'campi.gst.service'

    def __init__(self):
        super().__init__([T.CAMERA_RTMP, T.CAMERA_OVERLAY, T.CAMERA_IMAGE])
        self.config = self._read_config()
        if self.config.get('RTMP_ENABLE', True):
            util_start_service(self.SNAME)
        self.is_running = util_check_service(self.SNAME)

    def _read_config(self):
        config = {}
        with open(GST_CONFIG_PATH, 'r') as fr:
            for line in fr.readlines():
                line = line.strip()
                if line and line[0] != '#':
                    key, value = line.split('=')
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    config[key] = value
        return config

    def _save_config(self, config):
        with open(GST_CONFIG_PATH, 'w') as fw:
            for key, value in config.items():
                fw.write(f"{key}={value}\n")

    def set_config(self, jdata):
        to_save = False
        for key, value in jdata.items():
            key = key.upper()
            if key in self.config and value != self.config[key]:
                self.config[key] = value
                to_save = True
        if to_save:
            self._save_config()
        return to_save

    def get_rtmp_config(self):
        return {
            "rtmp_enable": self.config.get('RTMP_ENABLE', True),
            "rtmp_domain": self.config.get('RTMP_DOMAIN', 'srs.hzcsdata.com'),
            "rtmp_room": self.config.get('RTMP_ROOM', 'live'),
            "rtmp_stream": self.config.get('RTMP_STREAM', ADDRESS),
            "rtmp_vhost": self.config.get('RTMP_VHOST', 'seg.300s')
        }

    def _set_rtmp(self, jdata):
        self.set_config(jdata)
        enable = self.config.get('RTMP_ENABLE', True)
        if enable:
            if not self.is_running:
                util_start_service(self.SNAME)
        else:
            if self.is_running:
                util_stop_service(self.SNAME)

        self.is_running = util_check_service(self.SNAME)
        self.send_message(T.CAMERA_CONFIG, self.get_rtmp_config())

    def get_overlay_config(self):
        return {
            "time_format": self.config.get('TIME_FORMAT', "%Y/%m/%d %H:%M:%S"),
            "time_halignment": self.config.get('TIME_HALIGNMENT', 'right'),
            "time_valignment": self.config.get('TIME_VALIGNMENT', 'top'),
            "text_title": self.config.get('TEXT_TITLE', 'auto'),
            "text_halignmen": self.config.get('TEXT_HALIGNMEN', 'left'),
            "text_valignment": self.config.get('TEXT_VALIGNMENT', 'top'),
        }

    def _set_overlay(self, jdata):
        if self.set_config(jdata):
            if self.is_running:
                util_start_service(self.SNAME, restart=True)
            self.is_running = util_check_service(self.SNAME)
        self.send_message(T.CAMERA_CONFIG, self.get_overlay_config())

    def get_image_config(self):
        return {
            'frame_width': int(self.config.get('FRAME_WIDTH', '640')),
            'frame_height': int(self.config.get('FRAME_HEIGHT', '480')),
            'frame_rate': int(self.config.get('FRAME_RATE', '15')),
            'brightness': int(self.config.get('BRIGHTNESS', '0')),
            'contrast': int(self.config.get('CONTRAST', '0')),
            'hue': int(self.config.get('HUE', '0')),
            'saturation': int(self.config.get('SATURATION', '0')),
            'flip_method': self.config.get('FLIP_METHOD', 'vertical-flip'),
        }

    def _set_image(self, jdata):
        if self.set_config(jdata):
            if self.is_running:
                util_start_service(self.SNAME, restart=True)
            self.is_running = util_check_service(self.SNAME)
        self.send_message(T.CAMERA_CONFIG, self.get_image_config())

    def do_report_config(self):
        config = {
            'rtmp': self.get_rtmp_config(),
            'overlay': self.get_overlay_config(),
            'image': self.get_image_config()
        }
        self.send_message(T.CAMERA_CONFIG, config)

    def handle_message(self, topic, message):
        self.logger.info(f'gst {topic} {message}')
        jdata = json.loads(message)

        if topic == T.CAMERA_RTMP:
            return self._set_rtmp(jdata)

        if topic == T.CAMERA_OVERLAY:
            return self._set_overlay(jdata)

        if topic == T.CAMERA_IMAGE:
            return self._set_image(jdata)
