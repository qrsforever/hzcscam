#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file base.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-20 20:48


import asyncio


class AsyncFatalError(Exception):
    pass


class AsyncTask(object):
    async def run(self):
        raise NotImplementedError

    def create_task(self):
        return asyncio.create_task(self.run())

    def __await__(self):
        return self.run().__await__()
