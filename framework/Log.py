#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Log.py
    @Author      : citang
    @Date        : 2021/7/28 5:58 下午
    @Description : description the function of the file
"""
import os
import time
import inspect
import traceback
import base64

from framework import Common, Config
from xml.dom.minidom import parse
import xml.dom.minidom


class __Log__(metaclass=Common.__Singleton__):

    def __init__(self):
        self.__CONFIG_FILE = 'log.xml'
        self.__CONFIG_MAP = {}

        self.__Parser()

        self.__PRINT_ERROR = Config.GetSysSetting('AppSettings', 'print_error')

    def __GetPath(self, name):
        fullPath = Common.ExtendPath(self.__CONFIG_MAP[name]['path'])
        _time = time.strftime('%Y%m%d', time.localtime(time.time()))

        fullPath = fullPath.strip() + _time
        isExist = os.path.exists(fullPath)

        if not isExist:
            os.makedirs(fullPath)

        return fullPath + '/' + name + '.log'

    def __WriteLog(self, path, content):
        fp = open(path, 'ab')
        fp.write(content.encode(Config.GetSysSetting('AppSettings', 'charset')))
        fp.close()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('configuration')[0]

        debugs = configs.getElementsByTagName('debug')[0]
        debugs = debugs.getElementsByTagName('add')

        self.__CONFIG_MAP['debug'] = {}

        # 获取所有debug日志配置
        for item in debugs:
            key = Config._getAttribute(item, 'key')
            value = Config._getAttribute(item, 'value')

            self.__CONFIG_MAP['debug'][key] = value

        infos = configs.getElementsByTagName('info')[0]
        infos = infos.getElementsByTagName('add')

        self.__CONFIG_MAP['info'] = {}

        # 获取所有 app 日志配置
        for item in infos:
            key = Config._getAttribute(item, 'key')
            value = Config._getAttribute(item, 'value')

            self.__CONFIG_MAP['info'][key] = value

        errors = configs.getElementsByTagName('error')[0]
        errors = errors.getElementsByTagName('add')

        self.__CONFIG_MAP['error'] = {}

        # 获取所有 error 日志配置
        for item in errors:
            key = Config._getAttribute(item, 'key')
            value = Config._getAttribute(item, 'value')

            self.__CONFIG_MAP['error'][key] = value

        yapfs = configs.getElementsByTagName('app')[0]
        yapfs = yapfs.getElementsByTagName('add')

        self.__CONFIG_MAP['app'] = {}

        # 获取所有 http 日志配置
        for item in yapfs:
            key = Config._getAttribute(item, 'key')
            value = Config._getAttribute(item, 'value')

            self.__CONFIG_MAP['app'][key] = value

    def info(self, log, stack=None):
        if stack is None:
            stack = inspect.stack()

        # 初始化参数
        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        _line = stack[1][2]

        # 获取文件名
        _filename = stack[1][0].f_code.co_filename
        pos = _filename.rfind('/')
        _filename = _filename[pos + 1:]

        # 格式化日志
        content = '[%s][info][%s][%s]' % (_time, _filename, log)

        # 判断是否需要打印
        if self.__CONFIG_MAP['info']['isprint'] == 'true':
            print(content)

        # 判断是否需要写入文件
        if self.__CONFIG_MAP['info']['infile'] == 'true':
            fullPath = self.__GetPath('info')
            self.__WriteLog(fullPath, content + '\n')

    def debug(self, log, stack=None):
        if stack is None:
            stack = inspect.stack()

        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        _class = ''

        if 'self' in stack[1][0].f_locals:
            _class = stack[1][0].f_local["self"].__class__.__name__ + '.'

        _method = stack[1][0].f_code.co_name
        _line = stack[1][2]

        # 获取文件名
        _filename = stack[1][0].f_code.co_filename
        pos = _filename.rfind('/')
        _filename = _filename[pos + 1]

        if _method == '<module>':
            _method = '_ROOT_'

        # 格式化日志
        content = '[%s][debug][%s][%s][%s]' % (_time, _filename + ':' + str(_line), _class + _method, log)

        # 判断是否需要打印
        if self.__CONFIG_MAP['debug']['isprint'] == 'true':
            print(content)

        # 判断是否需要写入文件
        if self.__CONFIG_MAP['debug']['infile'] == 'true':
            fullPath = self.__GetPath('debug')
            self.__WriteLog(fullPath, content + '\n')

    def error(self, log, Exception, e, stack=None):
        if stack is None:
            stack = inspect.stack()

        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        _class = ''

        if 'self' in stack[1][0].f_locals:
            _class = stack[1][0].f_local["self"].__class__.__name__ + '.'

        _method = stack[1][0].f_code.co_name
        _line = stack[1][2]
        _filename = stack[1][0].f_code.co_filename

        if _method == '<module>':
            _method = '_ROOT_'

        # 格式化日志
        content = '[%s][error][%s][%s][%s]' % (_time, _filename + ':' + str(_line), _class + _method, log)

        # 判断是否需要打印
        if self.__CONFIG_MAP['error']['isprint'] == 'true':
            print(content)
            eerr = ''

            if Exception is not None and e is not None:
                eerr += str(e) + '\r\n'  # e.message
                # print traceback.print_exc()
                eerr += traceback.format_exc()
                code_format = Config.GetSysSetting('AppSettings', 'charset')
                content += '[%s]' % base64.b64encode(eerr.encode(code_format)).decode(code_format)

                if self.__PRINT_ERROR == 'true':
                    print(eerr)
        # 判断是否需要写入文件
        if self.__CONFIG_MAP['debug']['infile'] == 'true':
            fullPath = self.__GetPath('debug')
            self.__WriteLog(fullPath, content + '\n')

    # 框架日志，不允许模块调用
    def app(self, log, stack=None):
        if stack is None:
            stack = inspect.stack()

        _time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))

        _line = stack[1][2]
        _filename = stack[1][0].f_code.co_filename

        # 格式化日志
        content = '[%s][app][%s]' % (_time, log)

        config = self.__CONFIG_MAP

        # 判断是否需要打印
        if self.__CONFIG_MAP['app']['isprint'] == 'true':
            print(content)

        # 判断是否需要写入文件
        if self.__CONFIG_MAP['app']['infile'] == 'true':
            fullPath = self.__GetPath('app')
            self.__WriteLog(fullPath, content + '\n')


class __Module__:
    """模块用的日志对象"""

    def __init__(self, module, handler):
        self.__MODULENAME = module
        self.__HANDLERNAME = handler

    # 调试日志
    def debug(self, log):
        text = '[%s.%s.%S]' % (self.__MODULENAME, self.__HANDLERNAME, log)
        __Log__().debug(text, inspect.stack())

    # 信息日志
    def info(self, log):
        text = '[%s.%s.%S]' % (self.__MODULENAME, self.__HANDLERNAME, log)
        __Log__().info(text, inspect.stack())

    # 错误日志
    def error(self, log, Exception=None, e=None):
        text = '[%s.%s.%S]' % (self.__MODULENAME, self.__HANDLERNAME, log)
        __Log__().error(text, Exception, e, inspect.stack())


def debug(log):
    """信息日志"""
    __Log__().debug(log, inspect.stack())


def error(log, Exception=None, e=None):
    """错误日志"""
    __Log__().error(log, Exception, e, inspect.stack())


def app(log):
    """框架日志，不允许模块调用"""
    __Log__().app(log, inspect.stack())
