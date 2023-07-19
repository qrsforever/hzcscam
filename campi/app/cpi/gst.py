#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file gst.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-06-15 15:01

import subprocess
import os
import json

from campi.utils.shell import util_get_uptime
from . import MessageHandler
from campi.constants import (
    ADDRESS, SVC_GST,
    GST_CAMERA_PROP,
    GST_CONFIG_PATH,
)

from campi.utils.shell import (
    util_check_service,
    util_start_service,
    util_stop_service,
)

from campi.topics import (
    TCloud,
    TUsbCamera,
)


class GstMessageHandler(MessageHandler):

    SNAME = SVC_GST
    DEFAULT_VID = '/dev/video1'

    def __init__(self):
        super().__init__([
            TUsbCamera.ALL,
            TCloud.CAMERA_RTMP, TCloud.CAMERA_OVERLAY, TCloud.CAMERA_IMAGE, TCloud.CAMERA_VIDEO,
        ])
        self.is_running = util_check_service(self.SNAME)
        self.config = self._read_config()
        if os.path.exists(self.DEFAULT_VID):
            if util_get_uptime() < 60:
                self.on_camera_plugin(self.DEFAULT_VID)

    def _restart_gst(self):
        if self.config.get('RTMP_ENABLE', True):
            util_start_service(self.SNAME, restart=True)

# Read & Save Config {{{
    def _read_config(self):
        config = {}
        with open(GST_CONFIG_PATH, 'r') as fr:
            for line in fr.readlines():
                line = line.strip()
                if line and line[0] != '#':
                    key, value = line.split('=')
                    if '#' in value:
                        value = value.split('#')[0].strip()
                    if value == 'true':
                        value = True
                    elif value == 'false':
                        value = False
                    config[key] = value
        return config

    def _save_config(self, config):
        with open(GST_CONFIG_PATH, 'w') as fw:
            for key, value in config.items():
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                fw.write(f"{key}={value}\n")

    def set_config(self, jdata):
        to_save = False
        for key, value in jdata.items():
            key = key.upper()
            if key in self.config and value != self.config[key]:
                self.config[key] = value
                to_save = True
        if to_save:
            self._save_config(self.config)
        else:
            self.logger.warn("same config, not restart gst")
        return to_save
# }}}

    def get_rtmp_config(self):# {{{
        return {
            "rtmp_enable": self.config.get('RTMP_ENABLE', True),
            "rtmp_domain": self.config.get('RTMP_DOMAIN', 'srs.hzcsdata.com'),
            "rtmp_room": self.config.get('RTMP_ROOM', 'live'),
            "rtmp_stream": self.config.get('RTMP_STREAM', ADDRESS),
            "rtmp_vhost": self.config.get('RTMP_VHOST', 'seg.300s')
        }

    def _set_rtmp(self, jdata):
        self.set_config(jdata)
        self.logger.info(f'{self.config}')
        enable = self.config.get('RTMP_ENABLE', True)
        if enable:
            if not self.is_running:
                self.logger.info(f'start {self.SNAME}')
                util_start_service(self.SNAME)
        else:
            if self.is_running:
                self.logger.info(f'stop {self.SNAME}')
                util_stop_service(self.SNAME)

        self.is_running = util_check_service(self.SNAME)
        self.send_message(TCloud.CAMERA_CONFIG, self.get_rtmp_config())
# }}}

    def get_overlay_config(self):# {{{
        return {
            "time_format": self.config.get('TIME_FORMAT', "%Y/%m/%d %H:%M:%S"),
            "time_halignment": self.config.get('TIME_HALIGNMENT', 'right'),
            "time_valignment": self.config.get('TIME_VALIGNMENT', 'top'),
            "text_title": self.config.get('TEXT_TITLE', 'auto'),
            "text_halignmen": self.config.get('TEXT_HALIGNMEN', 'left'),
            "text_valignment": self.config.get('TEXT_VALIGNMENT', 'top'),
            "text_sensor_count": self.config.get('TEXT_SENSOR_COUNT', False),
        }

    def _set_overlay(self, jdata):
        if self.set_config(jdata):
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, self.get_overlay_config())
# }}}

    def get_image_config(self):# {{{
        return {
            'frame_width': int(self.config.get('FRAME_WIDTH', '640')),
            'frame_height': int(self.config.get('FRAME_HEIGHT', '480')),
            'frame_rate': int(self.config.get('FRAME_RATE', '15')),
            'brightness': int(self.config.get('BRIGHTNESS', '100')),
            'contrast': int(self.config.get('CONTRAST', '50')),
            'hue': int(self.config.get('HUE', '50')),
            'saturation': int(self.config.get('SATURATION', '50')),
            'flip_method': self.config.get('FLIP_METHOD', 'none'),
        }

    def _set_image(self, jdata):
        if self.set_config(jdata):
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, self.get_image_config())
# }}}

    def get_video_config(self):# {{{
        return {
            "video_bitrate": int(self.config.get('VIDEO_BITRATE', 600)),
            "video_tune": self.config.get('VIDEO_TUNE', "zerolatency"),
            "video_pass": self.config.get('VIDEO_TUNE', "qual"),
            "video_speed_preset": self.config.get("VIDEO_SPEED_PRESET", "medium"),
            "video_quantizer": int(self.config.get("VIDEO_QUANTIZER", 30)),
            "video_profile": self.config.get("VIDEO_PROFILE", "none"),
        }

    def _set_video(self, jdata):
        if self.set_config(jdata):
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, self.get_video_config())
# }}}

    def on_camera_plugin(self, videoid):# {{{
        try:
            ret = subprocess.Popen(
                    f'v4l2-ctl --device {videoid} --list-ctrls',
                    shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
            if not ret.returncode:
                config = {}
                for line in ret.stdout.readlines():
                    line = line.strip()
                    if not line or ':' not in line:
                        continue
                    p, q = line.split(':')
                    p, q = p.strip(), q.strip()
                    psegs = p.split(' ')
                    if psegs[0] in ('brightness', 'contrast', 'hue', 'saturation'):
                        qsegs = q.split(' ')
                        props = {'min': 0, 'max': 1, 'step': 1}
                        if psegs[-1] == '(int)':
                            for i, name in enumerate(['min', 'max', 'step', 'default', 'value']):
                                props[name] = int(qsegs[i].split('=')[1])
                        config[psegs[0]] = props
                with open(GST_CAMERA_PROP, 'w') as fw:
                    json.dump(config, fw)
            self._restart_gst()
        except Exception as err:
            self.logger.error(f'{err}')
# }}}

    def on_camera_plugout(self, videoid):# {{{
        if os.path.isfile(GST_CAMERA_PROP):
            os.unlink(GST_CAMERA_PROP)
# }}}

    def get_info(self):# {{{
        config = {
            "gst": {
                'rtmp': self.get_rtmp_config(),
                'overlay': self.get_overlay_config(),
                'image': self.get_image_config(),
                'video': self.get_video_config(),
            }
        }
        self.logger.info(f'gst config: {config}')
        return config
# }}}

    def handle_message(self, topic, message):
        self.logger.info(f'gst {topic} {message}')

        if topic == TUsbCamera.PLUGIN:
            return self.on_camera_plugin(message)

        if topic == TUsbCamera.PLUGOUT:
            return self.on_camera_plugout(message)

        jdata = json.loads(message)

        if topic == TCloud.CAMERA_RTMP:
            return self._set_rtmp(jdata)

        if topic == TCloud.CAMERA_OVERLAY:
            return self._set_overlay(jdata)

        if topic == TCloud.CAMERA_IMAGE:
            return self._set_image(jdata)

        if topic == TCloud.CAMERA_VIDEO:
            return self._set_video(jdata)
