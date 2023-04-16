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

    pipeline = Gst.Pipeline.new("campi")

    def make(self, plug, name):
        element = Gst.ElementFactory.make(plug, name)
        self.pipeline.add(element)
        return element
