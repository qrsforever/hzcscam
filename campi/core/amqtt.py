#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file amqtt.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-24 19:30


import sys
import os
import asyncio
import paho.mqtt.client as paho_mqtt
from campi.topics import tLogger as LOG
from campi.constants import MAIN_PID


def log_prefix():
    frame = sys._getframe().f_back.f_back
    filename = os.path.basename(frame.f_code.co_filename)
    funcname = frame.f_code.co_name
    lineno = frame.f_lineno
    return '[{}] {} {}:{}'.format(MAIN_PID, filename, funcname, lineno)


class MqttError(Exception):
    def __init__(self, rc):
        self.rc = rc


class AsyncMqtt(object):
    def __init__(self, client_id, loop):
        self.loop = loop
        self.misc_task = None
        self.client = paho_mqtt.Client(client_id)
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_socket_open = self._on_socket_open
        self.client.on_socket_close = self._on_socket_close
        self.client.on_socket_register_write = self._on_socket_register_write
        self.client.on_socket_unregister_write = self._on_socket_unregister_write  # noqa
        self.message_callback = None
        self._connected = asyncio.Future()
        self.ok = False

    def _on_socket_open(self, client, userdata, sock):
        print('_on_socket_open sock:', sock)
        self.loop.add_reader(sock, client.loop_read)

        def _do_socket_open():
            self.misc_task = self.loop.create_task(self.misc_loop())

        self.loop.call_soon_threadsafe(_do_socket_open)

    def _on_socket_close(self, client, userdata, sock): 
        self.loop.remove_reader(sock)
        if self.misc_task is not None:
            self.misc_task.cancel()

    def _on_socket_register_write(self, client, userdata, sock):
        self.loop.add_writer(sock, client.loop_write)

    def _on_socket_unregister_write(self, client, userdata, sock):
        self.loop.remove_writer(sock)

    async def misc_loop(self) -> None:
        while self.client.loop_misc() == paho_mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    def _on_connect(self, client, userdata, flags, rc):
        if self._connected.done():
            return
        if rc == paho_mqtt.CONNACK_ACCEPTED:
            print("Connected to MQTT Broker!")
            # self.client.subscribe('/logger/#')
            self._connected.set_result(rc)
            self.ok = True
        else:
            print("Failed to connect, return code {rc}".format(rc=rc))
            self._connected.set_exception(MqttError(rc))

    def connect_sync(self, host='127.0.0.1', port=1883):
        return self.client.connect(host, port)

    async def connect(self, host='127.0.0.1', port=1883, timeout=5):
        await self.loop.run_in_executor(None, self.client.connect, host, port)
        await asyncio.wait_for(self._connected, timeout=timeout)

    def _on_message(self, client, userdata, message):
        # print("[{current_thread}]: Received `{payload}` from `{topic}` topic".format(
        #     current_thread=threading.current_thread().ident,
        #     payload=message.payload.decode(),
        #     topic=message.topic))
        if self.message_callback:
            self.message_callback(message.topic, message.payload.decode())

    def subscribe(self, topics, callback=None):
        if isinstance(topics, str):
            topics = [topics]
        for topic in topics:
            self.client.subscribe(topic)
        if callback is not None:
            self.message_callback = callback

    def publish(self, topic, message, qos=0):
        if self.ok:
            return self.client.publish(topic, message, qos)

    def logd(self, message):
        print(message)
        if self.ok:
            self.client.publish(LOG.DEBUG, f'{log_prefix()} - {message}')

    def logi(self, message):
        print(message)
        if self.ok:
            self.client.publish(LOG.INFO, f'{log_prefix()} - {message}')

    def logw(self, message):
        print(message)
        if self.ok:
            self.client.publish(LOG.WARN, f'{log_prefix()} - {message}')

    def loge(self, message):
        print(message)
        if self.ok:
            self.client.publish(LOG.ERROR, f'{log_prefix()} - {message}')
