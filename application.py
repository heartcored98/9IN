# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify
from response import *

app = Flask(__name__)


@app.route('/keyboard')
def Keyboard():
    dataSend = {
        "type": "buttons",
        "buttons": ["구이니와 돈벌기", "도움말"]
    }
    return jsonify(dataSend)


@app.route('/message', methods=['POST'])
def Message():
    dataReceive = request.get_json()
    content = dataReceive['content']
    response = get_response(content)
    return jsonify(response)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')

