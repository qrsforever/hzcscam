#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file network.py
# @brief
# @author QRS
# @version 1.0
# @date 2023-04-26 22:49


from quart import Blueprint, request, Response


api_network = Blueprint("network", __name__)


@api_network.route('/save', methods=['POST'])
async def _set_network():
    pass

@api_network.route('/wifi', methods=['POST'])
async def _set_wifi():
    form = await request.form
    wifissid = form['wifissid']
    password = form['password']
    print(wifissid, password)
    return Response(status=200)
