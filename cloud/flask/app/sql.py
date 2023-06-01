#!/usr/bin/python3
# -*- coding: utf-8 -*-

import inspect
import json
from abc import ABC, abstractmethod
from utils import convert_timestamp_to_datetime

class TableBase(ABC):

    def __new__(cls, *arg, **kwargs):
        parent_coros = inspect.getmembers(TableBase, predicate=inspect.iscoroutinefunction)

        for coro in parent_coros:
            child_method = getattr(cls, coro[0])
            if not inspect.iscoroutinefunction(child_method):
                raise RuntimeError('The method %s must be a coroutine' % (child_method,))

        return super(TableBase, cls).__new__(cls)

    def __init__(self, dbpool, logger):
        self.dbpool = dbpool
        self.logger = logger

    @abstractmethod
    async def insert(self, jdata):
        pass

    async def execute(self, sql, values):
        # self.logger.info(sql)
        async with self.dbpool.acquire() as conn:
            cursor = await conn.cursor()
            await cursor.execute(sql, values)
            await conn.commit()


class TableMessagePublish(TableBase):
    feilds = (
        'id', 'clientid', 'username',
        'topic', 'peerhost', 'node', 'payload',
        'flags', 'qos', 'publish_received_at'
    )
    colnum = len(feilds)
    tabel_name = 'message_publish'

    async def insert(self, jdata):
        if not isinstance(jdata, dict):
            self.logger.warn(f'data not support: {jdata}')
            return
        feilds, values = [], []
        for key, val in jdata.items():
            if key not in self.feilds:
                continue
            if key == 'publish_received_at':
                val = convert_timestamp_to_datetime(val / 1000)
            if isinstance(val, dict):
                val = json.dumps(val)
            feilds.append(key)
            values.append(val)
        sql = 'insert into %s(%s) values(%s)' % (
            self.tabel_name, ','.join(feilds), ','.join(["%s"] * len(feilds)))
        await self.execute(sql, values)

class TableClientConnected(TableBase):
    feilds = (
        'clientid', 'username', 'sockname', 'peername',
        'node', 'receive_maximum', 'keepalive', 'expiry_interval',
        'is_bridge', 'clean_start', 'proto_name', 'proto_var', 'connected_at'
    )
    colnum = len(feilds)
    tabel_name = 'client_connected'

    async def insert(self, jdata):
        if not isinstance(jdata, dict):
            self.logger.warn(f'data not support: {jdata}')
            return
        feilds, values = [], []
        for key, val in jdata.items():
            if key not in self.feilds:
                continue
            if key == 'connected_at':
                val = convert_timestamp_to_datetime(val / 1000)
            if isinstance(val, dict):
                val = json.dumps(val)
            feilds.append(key)
            values.append(val)
        sql = 'insert into %s(%s) values(%s)' % (
            self.tabel_name, ','.join(feilds), ','.join(["%s"] * len(feilds)))
        await self.execute(sql, values)

class TableClientDisconnected(TableBase):
    feilds = (
        'id', 'clientid', 'username',
        'reason', 'disconnected_at'
    )
    colnum = len(feilds)
    tabel_name = 'client_disconnected'

    async def insert(self, jdata):
        if not isinstance(jdata, dict):
            self.logger.warn(f'data not support: {jdata}')
            return
        feilds, values = [], []
        for key, val in jdata.items():
            if key not in self.feilds:
                continue
            if key == 'disconnected_at':
                val = convert_timestamp_to_datetime(val / 1000)
            if isinstance(val, dict):
                val = json.dumps(val)
            feilds.append(key)
            values.append(val)
        sql = 'insert into %s(%s) values(%s)' % (
            self.tabel_name, ','.join(feilds), ','.join(["%s"] * len(feilds)))
        await self.execute(sql, values)
