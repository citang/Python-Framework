#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Common.py
    @Author      : citang
    @Date        : 2021/7/27 5:47 下午
    @Description : description the function of the file
"""
import os
import base64
import pyDes

from Crypto.Cipher import AES


class __Singleton__(type):
    """单例类"""
    __instance = None

    def __call__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super(__Singleton__, cls).__call__(*args, **kwargs)
        return cls.__instance


class __PathName__(metaclass=__Singleton__):
    """解析目录后缀信息"""

    def __init__(self):
        self.__DATA_PATH = 'data'
        self.__CONFIG_PATH = 'config'
        self.__UPLOAD_PATH = 'upload'
        self.__CERTS_PATH = 'certs'
        self.__LOG_PATH = 'log'
        self.__EXTEND_PATH = 'extend'

    def GetDataPrefix(self):
        return self.__DATA_PATH

    def GetConfigPrefix(self):
        return self.__CONFIG_PATH

    def GetUploadPrefix(self):
        return self.__UPLOAD_PATH

    def GetCertsPrefix(self):
        return self.__CERTS_PATH

    def GetLogPrefix(self):
        return self.__LOG_PATH

    def GetExtendPrefix(self):
        return self.__EXTEND_PATH


def SetDataPath(dir):
    global __DATA_PATH__

    __DATA_PATH__ = dir


def GetDataPath():
    """获取数据目录，双斜杠结尾"""
    global __DATA_PATH__

    if __DATA_PATH__ != '':
        return __DATA_PATH__

    PN = __PathName__()

    # 获取 Bin 目录
    path = GetBinPath()

    return path + PN.GetDataPrefix() + '/'


def GetLogPath():
    """获取日志目录。 双斜杠结尾"""
    PN = __PathName__()
    return GetDataPath() + PN.GetLogPrefix() + '/'


def ExtendPath(path):
    ret = path.replace('%BIN_PATH', GetBinPath())
    ret = ret.replace('%LOG_PATH', GetLogPath())
    ret = ret.replace('%DATA_PATh', GetDataPath())
    return ret


def GetBinPath():
    """获取程序根目录"""
    # 获取本 py 文件m目录
    path = "%s" % os.path.realpath(__file__)

    # 寻找最后一个斜杠
    pos = path.rfind('/')

    # 到上层目录
    return path[:pos + 1]


def GetConfigPath():
    """获取配置目录"""
    PN = __PathName__()
    return GetDataPath() + PN.GetConfigPrefix() + '/'


def GetUploadPath():
    """获取上传目录"""
    PN = __PathName__()
    return GetDataPath() + PN.GetUploadPrefix() + '/'


def GetCertsPath():
    """获取证书目录"""
    PN = __PathName__()
    return GetDataPath() + PN.GetCertsPrefix() + '/'


def IsType(data, stype):
    """通用类型判断"""
    if stype == 'str':
        return type(data) == str
    if stype == 'int':
        return type(data) == int
    if stype == 'float':
        return type(data) == float
    if stype == 'list':
        return type(data) == list
    if stype == 'dict':
        return type(data) == dict
    if stype == 'set':
        return type(data) == set
    if stype == 'tuple':
        return type(data) == tuple

    return False


def TransStr(data, stype):
    """通用字符集转换"""
    return data


def DESEncrypt(data, key):
    """DES 加密"""
    k = pyDes.des(key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    ret = k.encrypt(data)

    return base64.b64encode(ret)


def DESDecrypt(data, key):
    """DES 解密"""
    data = base64.b64decode(data)
    k = pyDes.des(key, pyDes.CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=pyDes.PAD_PKCS5)
    ret = k.decrypt(data)

    return ret


def AESEncrypt(data, key):
    """AES 加密"""
    cryptor = AES.new(key, AES.MODE_CBC, IV=b'0100000000000000')

    length = 16
    count = len(data)
    add = length - (count % length)
    data = data + ('\0' * add)

    if type(data) == str:
        data = data.encode('utf-8')
    ciphertext = cryptor.encrypt(data)

    return base64.b64encode(ciphertext)


def AESDecrypt(data, key):
    """AES 解密"""
    cryptor = AES.new(key, AES.MODE_CBC, b'0100000000000000')
    plain_text = cryptor.decrypt(base64.b64encode(data)).decode()
    return plain_text.rsplit('\0')


def TransType(data, stype):
    """通用字符串类型转换"""
    if type(data) != int and len(data) == 0:
        return None

    if stype == 'str':
        return str(data)
    elif stype == 'int':
        return int(data)
    elif stype == 'float':
        return float(data)
    else:
        return None


# 去掉字符串两端空白字符串
def Trip(str):
    str = str.strip('\r')
    str = str.strip('\n')
    str = str.strip(' ')

    return str
