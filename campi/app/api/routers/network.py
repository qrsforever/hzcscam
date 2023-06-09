#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file network.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-26 22:49


import json
from quart import Blueprint, request, Response
from quart import current_app as app
from campi.topics import TApis

api_network = Blueprint("network", __name__)

@api_network.route('/save', methods=['POST'])
async def _set_network():
    pass


@api_network.route('/set_wifi', methods=['POST'])
async def _set_wifi():
    form = await request.form
    wifissid = form['wifissid']
    password = form['password']

    jdata = json.dumps({'wifissid':wifissid, 'password': password})
    app.mqtt.logi(jdata)
    app.mqtt.publish(TApis.SET_WIFI, jdata)

    return Response(status=200)
