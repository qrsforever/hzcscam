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
    device = Unicode(default_value='/dev/video0', help='Source video device').tag(config=True)
    number_buffers = Int(default_value=-1, help='Number of buffers to output before sending EOS').tag(config=True)

    brightness = Int(default_value=0, help='Picture brightness').tag(config=True)
    contrast = Int(default_value=0, help='Picture contrast or luma gain').tag(config=True)
    hue = Int(default_value=0, help='Hue or color balance').tag(config=True)
    saturation = Int(default_value=0, help='Picture color saturation').tag(config=True)

    # width = Int(default_value=640, help='Source video frame width').tag(config=True)
    # height = Int(default_value=480, help='Source video frame height').tag(config=True)
    # framerate = Int(default_value=30, help='Source video frame rate').tag(config=True)

    def make(cls):
        pass
