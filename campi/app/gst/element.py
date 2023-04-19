#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file element.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-16 19:04

import gi # type: ignore
gi.require_version("Gst", "1.0")
from gi.repository import Gst # type: ignore

from traitlets.config.configurable import Configurable
from traitlets import Unicode


class GElement(Configurable):
    name = Unicode('')

    pipeline = Gst.Pipeline.new("campibin")

    def __init__(self, *args, **kwargs):
        super(GElement, self).__init__(*args, **kwargs)

    @classmethod
    def make(cls, plug, name=None):
        if plug == 'capsfilter':
            element = Gst.ElementFactory.make(plug, None)
            element.set_property('caps', Gst.Caps.from_string(name))
        else:
            element = Gst.ElementFactory.make(plug, name)
        cls.pipeline.add(element)
        return element

    @staticmethod
    def set(element, name, value):
        return element.set_property(name, value)
