#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import aiomysql
import logging
from quart import Quart, request, Response
from sql import TableMessagePublish, TableClientConnected, TableClientDisconnected

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

app = Quart(__name__)
app.dbpool = None

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
    except Exception:
        return Response(status=401)
    return Response(status=200)
# }}}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8686, use_reloader=False)
