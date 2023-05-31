#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import json
import aiomysql
import logging
from quart import Quart, request, Response

logging.basicConfig(level=logging.DEBUG)

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
    async with app.dbpool.acquire() as conn:
        cursor = await conn.cursor()
        app.logger.info(f'{type(jdata["qos"])}')
        if event == 'message.publish':
            await cursor.execute(
                'insert into message_publish values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                (
                    jdata['id'], jdata['username'], jdata['clientid'], jdata['qos'],
                    jdata['topic'], json.dumps(jdata['payload']), jdata['peerhost'],
                    jdata['publish_received_at'], jdata['timestamp'],
                    jdata['node'], json.dumps(jdata['flags'])
                ))
        await conn.commit()
    return Response(status=200)
# }}}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8686, use_reloader=False)
