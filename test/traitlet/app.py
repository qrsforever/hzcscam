#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file app.py
# @brief test traitlets app
# @author QRS
# @version 1.0
# @date 2023-04-14 16:16


from traitlets.config.application import Application
from traitlets import Bool, Unicode, List, Dict, Enum

class TestTraitletApp(Application):
    """
    This is a test case for traitlets app
    """

    name = Unicode('TestApp')
    description = Unicode(__doc__)
    config_file = Unicode('', help='Load app config file').tag(config=True)
