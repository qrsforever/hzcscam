#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file arguments.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-13 20:20


from dataclasses import dataclass
from simple_parsing import ArgumentParser, choice
from typing import Optional


@dataclass
class LoggerArgs():
    """
    LOG
    """
    log_path: Optional[str] = "/tmp/campi.log" 
    log_level: Optional[str] = choice("debug", "info", "warning", "error")
    log_format: Optional[str] = "%(thread)d %(asctime)s %(levelname)s %(message)s"

