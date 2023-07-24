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
# from campi.utils.easydict import DotDict
from . import MessageHandler
from campi.constants import (
    ADDRESS, SVC_GST,
    GST_CAMERA_PROP,
    GST_CONFIG_PATH,
    GST_CONFIG_SENV,
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
        if self.config['rtmp'].get('RTMP_ENABLE', True):
            util_start_service(self.SNAME, restart=True)

# Read & Save Config {{{
    def _read_config(self):
        config = {}
        with open(GST_CONFIG_PATH, 'r') as fr:
            config = json.load(fr)
        return config

    def _save_config(self, config):
        with open(GST_CONFIG_PATH, 'w') as fw:
            json.dump(config, fw)
            with open(GST_CONFIG_SENV, 'w') as sw:
                for _, jdata in config.items():
                    for key, value in jdata.items():
                        if isinstance(value, bool):
                            value = 'true' if value else 'false'
                        sw.write(f"{key.upper()}={value}\n")

    def set_config(self, key, jdata):
        changed = {}
        if key not in self.config:
            self.config[key] = {}

        config = self.config[key]
        for key, value in jdata.items():
            if key in config and value != config[key]:
                config[key] = value
                changed[key] = value
        if len(changed) > 0:
            self._save_config(self.config)
        else:
            self.logger.warn("same config, not restart gst")
        return changed
# }}}

    def get_rtmp_config(self):# {{{
        return self.config.get('rtmp', {})

    def _set_rtmp(self, jdata):
        changed = self.set_config('rtmp', jdata)
        self.logger.info(f'{changed}')
        enable = changed.get('rtmp_enable', True)
        if enable:
            if not self.is_running:
                self.logger.info(f'start {self.SNAME}')
                util_start_service(self.SNAME)
        else:
            if self.is_running:
                self.logger.info(f'stop {self.SNAME}')
                util_stop_service(self.SNAME)

        self.is_running = util_check_service(self.SNAME)
        self.send_message(TCloud.CAMERA_CONFIG, changed) 
# }}}

    def get_overlay_config(self):# {{{
        return self.config.get('overlay', {})

    def _set_overlay(self, jdata):
        changed = self.set_config('overlay', jdata)
        if len(changed) > 0:
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, changed)
# }}}

    def get_image_config(self):# {{{
        return self.config.get('image', {})

    def _set_image(self, jdata):
        changed = self.set_config('image', jdata)
        if len(changed) > 0:
            if set(changed.keys()).intersection(
                set(['frame_width', 'frame_height', 'frame_rate', 'flip_method'])): # noqa
                self._restart_gst()
            else:
                if os.path.exists(GST_CAMERA_PROP):
                    with open(GST_CAMERA_PROP, 'r') as fr:
                        props = json.load(fr)
                        for key, val in changed.items():
                            if key not in props.keys():
                                continue
                            max, min = props[key]['max'], props[key]['min']
                            val = int(val * (max - min) / 100 + min)
                            cmd = f'v4l2-ctl --device {self.DEFAULT_VID} --set-ctrl {key}={val}'
                            self.logger.info(cmd)
                            subprocess.run(cmd, shell=True, capture_output=False, encoding='utf-8')
            self.send_message(TCloud.CAMERA_CONFIG, changed)
# }}}

    def get_video_config(self):# {{{
        return self.config.get('video', {})

    def _set_video(self, jdata):
        changed = self.set_config('video', jdata)
        if len(changed) > 0:
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, changed)
# }}}

    def get_audio_config(self):# {{{
        return self.config.get('audio', {})
# }}}

    def _set_audio(self, jdata):# {{{
        changed = self.set_config('audio', jdata)
        if len(changed) > 0:
            self._restart_gst()
        self.send_message(TCloud.CAMERA_CONFIG, changed)
# }}}

    def on_camera_plugin(self, videoid):# {{{
        self.DEFAULT_VID = videoid
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
                'audio': self.get_audio_config(),
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

        if topic == TCloud.CAMERA_AUDIO:
            return self._set_AUDIO(jdata)
