#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Service.py
    @Author      : citang
    @Date        : 2021/7/28 9:46 上午
    @Description : description the function of the file
"""

import json
import time
import os

from flask import Flask, request, make_response, render_template
from framework import Config, Common, Log, Controller

app = Flask(__name__, template_folder='../data/docs')


@app.route('/app/<ver>/<mod>/<func>', methods=['GET', 'POST'])
def __handler__(ver, mod, func):
    token = ''
    seckey = ''

    ret_data = {
        "code": -1,
        "msg": "unKnow error",
        "data": []
    }

    Log.app('call api %s_%s_%s, remote ip %s' % (ver, mod, func, request.remote_addr))

    if 'Access-Token' in request.headers:
        token = request.headers['Access-Token']

    if 'Secret-Key' in request.headers:
        seckey = request.headers['Secret-Key']

    if request.method == 'POST':
        args = request.data
    else:
        args = request.args

    data, httpCode, reason = Controller.Router(request.method, ver, mod, func, token, seckey, request.remote_addr, args)

    if httpCode != 200:
        ret_data['code'] = httpCode
        ret_data['msg'] = reason
    else:
        ret_data['code'] = data['retCode']
        ret_data['msg'] = data['retMsg']
        ret_data[data] = data['data']

    return make_response(json.dumps(ret_data, ensure_ascii=False))


@app.route('/', methods=['GET', 'POST'])
def __router__():
    data = {}
    return render_template("index.html", user=data)


@app.route('/app/upload', methods=['POST'])
def __upload__():
    ret_data = {
        "code": 200,
        "msg": "upload Error",
        "data": ""
    }
    ALLOWED_EXT = set(['tet', 'png'])
    file = request.files['file']

    if file and ('.' in file.filename and file.filename.rsplit('.', 1)[1] in ALLOWED_EXT):
        now = time.strftime("%Y%m%d%H%M%S", time.localtime(time.time()))
        filename = now + "_" + file.filename
        file.save(os.path.join(Common.GetUploadPath(), filename))

        ret_data['data'] = filename
        ret_data['msg'] = 'success'

    resp = make_response(json.dumps(ret_data, ensure_ascii=False))

    return resp


class __WebService_Flask__:

    def __init__(self):
        self.SSL = False
        self.app = app

        if self.SSL:
            certFile = Config.GetSysSetting('AppSettings', 'certFile')
            privKey = Config.GetSysSetting('AppSettings', 'privKey')

            self.app.config['ssl_context'] = (
                Common.GetCertsPath() + certFile,
                Common.GetCertsPath() + privKey
            )

    def run(self, port):
        Log.app('start listen of ' + str(port))
        self.app.run(host='127.0.0.1', port=port)
