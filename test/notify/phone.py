#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import hashlib
from urllib.parse import quote_plus
from urllib.request import urlopen

DEBUG = False

PHONES = [
    '15801310416',
]

MSG_URI = 'http://115.231.168.138:8861'
UID = '966646'
CODE = '4YC3HDAZRO'
SRCPHONE = '88191008369646'


def main():
    report_context = '【TalentAI故障】xxx 验证码'

    report_data = []
    for tel in PHONES:
        report_data.append({
            "phone": tel,
            "context": report_context})
    msg = quote_plus(json.dumps(report_data, ensure_ascii=False, separators=(',', ':')))
    sign = hashlib.md5('{}{}'.format(msg, CODE).encode()).hexdigest()
    request = '{}?uid={}&msg={}&sign={}&srcphone={}'.format(MSG_URI, UID, msg, sign, SRCPHONE)
    urlopen(request)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(err)
