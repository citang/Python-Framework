#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Agent.py
    @Author      : citang
    @Date        : 2021/7/27 5:46 下午
    @Description : description the function of the file
"""
import sys

from framework import Model, Db, Log, Config, Common


class __Agent__:
    """模块功能"""

    def __init__(self, resultype, mod, handler, ip):

        self.__DATA = None
        self.__RESULTYPE = resultype
        self.__APICODE = 200

        self.__MODULENAME = mod
        self.__HANDLERNAME = handler
        self.__REMOTE_IP = ip

    def Data(self, name):
        """创建数据模型对象"""
        return Model.__ModelData__(name)

    def Db(self):
        """创建数据库对象"""
        return Db.__MysqlDb__()

    def Log(self):
        """创建日志对象"""
        return Log.__Module__(self.__MODULENAME, self.__HANDLERNAME)

    def __Cache(self):
        """创建缓存对象"""
        pass

    def GetAppConfig(self, group, name):
        """获取应用程序配置"""
        return Config.GetAppConfig(group, name)

    def GetSysConfig(self, group, name):
        """获取系统配置"""
        return Config.GetSysConfig(group, name)

    def SetApiCode(self, code):
        """设置API错误代码"""
        self.__APICODE = str(code)

    def GetApiCode(self):
        """获取API错误代码"""
        return self.__APICODE

    def GetRemoteIp(self):
        """获取请求IP"""
        return self.__REMOTE_IP

    def SetResult(self, data):
        """设置返回内容"""
        # 若没有设置RESULTYPE则不允许设置返回值
        if self.__RESULTYPE == '':
            raise Exception('resultype is empty, cant set result')

        # 检查数据格式
        if data is None:
            raise Exception('must not none of data')

        if data.GetName() != self.__RESULTYPE:
            raise Exception('router resultype different!')

        self.__DATA = data.DumpDict()

    def SetDictData(self, data):
        """设置返回内容"""
        if not isinstance(data, dict):
            raise Exception('data type must be dict')

        # 检查数据格式
        if data is None:
            raise Exception('must not none of data')

        self.__DATA = data

    def GetResult(self):
        return self.__DATA

    def ImportMod(self, mod):

        path = Common.ExtendPath(Config.GetSysConfig('AppSettings', 'module_path'))

        if '/' in mod:
            modPath = mod[0:mod.rfind('/')]
            sys.path.append(path + '/' + modPath)
            mod = mod[mod.rfind('/') + 1:]
        else:
            sys.path.append(path)

        impmod = __import__(mod)
        sys.path.pop()
        return impmod
