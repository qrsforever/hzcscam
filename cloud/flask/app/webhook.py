#!/usr/bin/python3
# -*- coding: utf-8 -*-

import asyncio
import logging
from quart import Quart, request, Response

logging.basicConfig(level=logging.DEBUG)

app = Quart(__name__)

@app.before_serving
async def startup():
    app.logger.error('aaaaa')
    loop = asyncio.get_running_loop()
    app.logger.info(f'{loop}')

@app.after_serving
async def shutdown():
    pass

@app.route("/mqtt", methods=['POST'])
async def _mqtt_msg():
    # app.logger.info(request.get_json())
    app.logger.info('aaaaaaaaaaaaaaa')
    return Response(status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8686, use_reloader=False)
