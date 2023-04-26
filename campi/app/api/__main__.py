#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file __main__.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-26 15:08


# import asyncio
from quart import Quart, render_template
from campi.constants import WS_ROOT 
from campi.app.api.routers import api_network

app = Quart(__name__, root_path=f'{WS_ROOT}/asset')
app.register_blueprint(api_network, url_prefix='/apis/network')


@app.before_serving
async def startup():
    pass


@app.after_serving
async def shutdown():
    pass


@app.route("/")
async def home():
    return await render_template("index.html")


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, use_reloader=False)
