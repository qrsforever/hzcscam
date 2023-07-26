#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import aiomysql
import logging
import json
import time
from quart import Quart, request, Response
from quart_cors import cors
from sql import TableMessagePublish, TableClientConnected, TableClientDisconnected

import paho.mqtt.client as mqtt

g_mqtt_client = None

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Quart(__name__)
app = cors(app, allow_origin="*")
app.dbpool = None
player_count = 0
player_last_time = int(time.time())

@app.before_serving
async def startup():# {{{
    # connect mysql
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db = os.getenv("DB_NAME")
    user_name = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    dbpool = await aiomysql.create_pool(
        autocommit=True, host=host, port=int(port),
        db=db, user=user_name, password=password)
    app.dbpool = dbpool
    async with dbpool.acquire() as conn:
        cursor = await conn.cursor()
        await cursor.execute("select @@version ")
        version = await cursor.fetchone()
        if version:
            app.logger.info(f'Running version: {version}')
        else:
            app.logger.info('Not connected.')

# }}}

@app.after_serving
async def shutdown():# {{{
    if app.dbpool is not None:
        app.dbpool.close()
        await app.dbpool.wait_closed()
# }}}

@app.route("/mqtt", methods=['POST'])
async def _mqtt_msg():# {{{
    jdata = await request.get_json()
    app.logger.info(f'{jdata}')
    event = jdata.get('event')
    try:
        if event == 'message.publish':
            table = TableMessagePublish(app.dbpool, app.logger)
            await table.insert(jdata)
        elif event == 'client.connected':
            table = TableClientConnected(app.dbpool, app.logger)
            await table.insert(jdata)
        elif event == 'client.disconnected':
            table = TableClientDisconnected(app.dbpool, app.logger)
            await table.insert(jdata)
    except Exception as err:
        app.logger.error(f'{err}')
        return Response(status=401)
    return Response(status=200)
# }}}

# cros (or POST -> OPTIONS)
@app.route("/rtmp", methods=['POST'])
async def _mqtt_rtmp_enable():# {{{
    global g_mqtt_client
    if g_mqtt_client is None:
        g_mqtt_client = mqtt.Client('flaskapp')
        g_mqtt_client.username_pw_set('campi', '123456')
        g_mqtt_client.connect('emqx', 1883, 60)
    try:
        jdata = await request.get_json()
        app.logger.info(f'{jdata}')
        did = jdata.get('stream')
        topic = f'cloud/{did}/camera/rtmp'
        payload = json.dumps({"rtmp_enable": jdata.get('enable')})
        g_mqtt_client.publish(topic=topic, payload=payload)
        app.logger.info('publish[%s]: [%s] ok!' % (topic, payload))
        return Response(status=200)
    except Exception as err:
        app.logger.error(f'{err}')
        return Response(status=401)
# }}}

@app.route("/apis/srs/v1/on_connect", methods=['POST'])
async def _srs_on_connnect():# {{{
    jdata = await request.get_json()
    app.logger.info(f'{jdata}')
    return '0'
# }}}

@app.route("/apis/srs/v1/on_close", methods=['POST'])
async def _srs_on_close():# {{{
    jdata = await request.get_json()
    app.logger.info(f'{jdata}')
    return '0'
# }}}

@app.route("/apis/srs/v1/on_play", methods=['POST'])
async def _srs_on_paly():# {{{
    global player_count
    current_time = int(time.time())
    if (current_time - player_last_time) > 21600: # 6 hours
        player_count = 0
    player_count += 1
    jdata = await request.get_json()
    app.logger.info(f'player count[{player_count}]: {jdata}')
    did = jdata.get('stream')
    topic = f'cloud/{did}/camera/rtmp'
    payload = json.dumps({"rtmp_enable": True})
    g_mqtt_client.publish(topic=topic, payload=payload)
    app.logger.info('publish[%s]: [%s] ok!' % (topic, payload))
    return '0'
# }}}

@app.route("/apis/srs/v1/on_stop", methods=['POST'])
async def _srs_on_stop():# {{{
    global player_count
    player_count -= 1
    jdata = await request.get_json()
    app.logger.info(f'player count[{player_count}]: {jdata}')
    if player_count <= 0:
        did = jdata.get('stream')
        topic = f'cloud/{did}/camera/rtmp'
        payload = json.dumps({"rtmp_enable": False})
        g_mqtt_client.publish(topic=topic, payload=payload)
        app.logger.info('publish[%s]: [%s] ok!' % (topic, payload))
        player_count = 0
    return '0'
# }}}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8686, use_reloader=False)
