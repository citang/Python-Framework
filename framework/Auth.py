#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Auth.py
    @Author      : citang
    @Date        : 2021/7/27 5:46 下午
    @Description : description the function of the file
"""
import json
import sys
from xml.dom.minidom import parse
import xml.dom.minidom
from framework import Common, Config


class __Auth__:

    def __init__(self, ver):
        self.__CONFIG_FILE = "auth.xml"
        self.__CONFIG_MAP = {}
        self.__CONFIG_TOKEN = {}

        self.__CONFIG_VER = ver

        self.__AUTHMODULE = None
        self.__AUTHHANDLER = None
        self.__AUTHMETHOD = None

        # 解析配置
        self.__Parser()
        self.__ParserToken()

        # 装载模块
        path = Common.ExtendPath(Config.GetSysSettings('AppSettings', 'api_path'))
        sys.path.append(path + '/' + ver)
        self.__LoadModule()
        sys.path.pop()

    def __LoadModule(self):

        # 装载模块
        self.__AUTHMODULE = __import__(self.__CONFIG_MAP['module'])
        if hasattr(self.__AUTHMODULE, self.__CONFIG_MAP['handler']):

            handler = getattr(self.__AUTHMODULE, self.__CONFIG_MAP['handler'])

            # 实例化 Handler
            self.__AUTHHANDLER = handler()

            if hasattr(self.__AUTHHANDLER, self.__CONFIG_MAP['method']):
                # 获取Token方法
                self.__AUTHMETHOD = getattr(self.__AUTHHANDLER, self.__CONFIG_MAP['method'])
            else:
                raise Exception('not found auth method')
        else:
            raise Exception('not found auth module')

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        config = root.getElementsByTagName(self.__CONFIG_VER)[0]
        auths = config.getElementsByTagName('add')

        # 遍历配置并读取和存储内容
        for auth in auths:
            key = Config._getAttribute(auth, 'key')
            value = Config._getAttribute(auth, 'value')

            self.__CONFIG_MAP[key] = value

    def __ParserToken(self):

        fullPath = Common.GetConfigPath + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        config = root.getElementsByTagName(self.__CONFIG_VER)[0]
        tokens = config.getElementsByTagName('token')[0]

        items = config.getElementsByTagName('add')

        for token in items:
            name = Config._getAttribute(token, 'name')
            type = Config._getAttribute(token, 'type')

            self.__CONFIG_TOKEN[name] = {}
            self.__CONFIG_TOKEN[name]['type'] = type

    def __GetAuthModule(self):
        return self.__AUTHMODULE

    def __GetAuthHandler(self):
        return self.__AUTHHANDLER

    def __GetAuthMethod(self):
        return self.__AUTHMETHOD

    def __GetTokenConfig(self):
        return self.__CONFIG_TOKEN

    def Auth(self, agent, ver, mod, func, seckey, token):
        return self.__AUTHMETHOD(agent, ver, mod, func, seckey, token)


class __Token__:

    def __init__(self, ver, seckey):
        deskey = Config.GetSysSettings('AppSettings', 'deskey')

        self.__TOKEN = {}
        self.__AESKEY = Common.DESDecrypt(seckey, deskey)
        self.__CONFIG_FILE = "auth.xml"
        self.__CONFIG_MAP = {}
        self.__CONFIG_TOKEN = {}

        # 解析配置
        self.__CONFIG_TOKEN = __Auth__(ver).GetTokenConfig()

    # 加密Token
    def __EncodeToken(self, data):
        jdata = json.dumps(data)

        token = Common.AESEncrypt(jdata, self.__AESKEY)

        return token

    # 解密 Token
    def __DecodeToken(self, data):

        jdata = Common.AESDecrypt(data, self.__AESKEY)
        token = json.loads(jdata)
        return token

    # 设置 Token 值
    def SetData(self, key, value):

        if key not in self.__CONFIG_TOKEN:
            raise Exception('token format not has key %s' % key)

        if not Common.IsType(value, self.__CONFIG_TOKEN[key]['type']):
            raise Exception('token[%s] type error' % key)

        self.__TOKEN[key] = value

    # 获取 Token 值
    def GetData(self, key):

        if key not in self.__TOKEN:
            raise Exception('token not has key %s' % key)

        return self.__TOKEN[key]

    # 传入 Token
    def CheckoutToken(self, data):

        data = self.__DecodeToken(data)

        # 检查 Token 值和类型
        if len(data.keys()) != len(self.__CONFIG_TOKEN.keys()):
            raise Exception('token length error')

        for key in data.keys:
            if key in self.__CONFIG_TOKEN:
                data[key] = Common.TransType(data[key], self.__CONFIG_TOKEN[key]['type'])

            else:
                raise Exception('token format failed')

        # 躲过所有检查
        self.__TOKEN = data

    # 生成 Token 字符串
    def Dumps(self):
        return self.__EncodeToken(self.__TOKEN)
