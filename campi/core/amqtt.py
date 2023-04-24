#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file amqtt.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-24 19:30


import threading
import asyncio
import paho.mqtt.client as paho_mqtt
from campi.utils.net import MAC


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
        self.client.on_socket_unregister_write = self._on_socket_unregister_write
        self.topics = []
        self.message_callback = None

    def _on_socket_open(self, client, userdata, sock):  # pyright: ignore
        # print('_on_socket_open sock:', sock)
        self.loop.add_reader(sock, client.loop_read)

        def _do_socket_open():
            self.misc_task = self.loop.create_task(self.misc_loop())

        self.loop.call_soon_threadsafe(_do_socket_open)

    def _on_socket_close(self, client, userdata, sock):  # pyright: ignore
        self.loop.remove_reader(sock)
        if self.misc_task is not None:
            self.misc_task.cancel()

    def _on_socket_register_write(self, client, userdata, sock):  # pyright: ignore
        self.loop.add_writer(sock, client.loop_write)

    def _on_socket_unregister_write(self, client, userdata, sock):  # pyright: ignore
        self.loop.remove_writer(sock)

    async def misc_loop(self) -> None:
        while self.client.loop_misc() == paho_mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break

    def _on_connect(self, client, userdata, flags, rc):  # pyright: ignore
        if rc == 0:
            print("Connected to MQTT Broker!")
            for topic in self.topics:
                self.client.subscribe(f'/{MAC}{topic}')
        else:
            print("Failed to connect, return code {rc}".format(rc=rc), )

    def _on_message(self, client, userdata, message):  # pyright: ignore
        print("[{current_thread}]: Received `{payload}` from `{topic}` topic".format(
            current_thread=threading.current_thread().ident,
            payload=message.payload.decode(),
            topic=message.topic))
        if self.message_callback:
            self.message_callback(message.topic, message.payload.decode())

    def subscribe(self, topics, callback):
        self.topics = topics
        self.message_callback = callback
        self.client.connect('127.0.0.1', 1883)

    def publish(self, topic, message, qos=0):
         return self.client.publish(f'/{MAC}{topic}', message, qos)
