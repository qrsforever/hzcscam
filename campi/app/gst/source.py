#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file source.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-16 19:33

from traitlets import Unicode, Int

from .element import GElement

class USBCamera(GElement):
    name = Unicode(default_value='usbcam')

    # v4l2src
    device = Unicode(default_value='/dev/video0', help='Source video device').tag(config=True)
    number_buffers = Int(default_value=-1, help='Number of buffers to output before sending EOS').tag(config=True)
    brightness = Int(default_value=0, help='Picture brightness').tag(config=True)
    contrast = Int(default_value=0, help='Picture contrast or luma gain').tag(config=True)
    hue = Int(default_value=0, help='Hue or color balance').tag(config=True)
    saturation = Int(default_value=0, help='Picture color saturation').tag(config=True)

    # capsfilter
    structure = Unicode(default_value='video/x-raw', help='Capabilities name').tag(config=True)
    format = Unicode(default_value='BGR', help='Capabilities format').tag(config=True)
    width = Int(default_value=640, help='Capabilities frame width').tag(config=True)
    height = Int(default_value=480, help='Capabilities frame height').tag(config=True)
    framerate = Int(default_value=30, help='Capabilities frame rate').tag(config=True)

    @staticmethod
    def create():
        camera = USBCamera()
        camera.rebuild()
        return camera

    def rebuild(self):
        self.source = self.make('v4l2src', self.name)
        self.source.set_property('device', self.device)
        self.source.set_property('number_buffers', self.number_buffers)
        self.source.set_property('brightness', self.brightness)
        self.source.set_property('contrast', self.contrast)
        self.source.set_property('hue', self.hue)
        self.source.set_property('saturation', self.saturation)
        self.filter = self.make('capsfilter', f'{self.structure},format=BGR,width={self.width},height={self.height},framerate={self.framerate}/1')
