#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Controller.py
    @Author      : citang
    @Date        : 2021/7/28 3:53 下午
    @Description : description the function of the file
"""
import json
import sys

from framework import Common, Config, Agent, Model, Log, Auth


class __SerializeData__:
    """处理返回数据"""

    def __init__(self):
        self.__DATA = None
        self.__RET = {'retcode': 200, 'retmsg': 'OK'}
        self.__HTTPCODE = 200
        self.__HTTPREASON = ''

    def SetRetCode(self, code, http_reason, errmsg):
        self.__RET['retcode'] = int(code)
        self.__RET['retmsg'] = errmsg

        self.__HTTPCODE = code
        self.__HTTPREASON = errmsg

    def GetHttpCode(self):
        return self.__HTTPCODE

    def GetHttpReason(self):
        return self.__HTTPREASON

    # 设置 API 错误代码
    def SetApiCode(self, code):
        apiMsg = Config.GetCodeById('apicode', str(code))
        if apiMsg is not None:
            self.__RET['retmsg'] = apiMsg

        # 约定 APICODE 为 STR 类型
        self.__RET['retcode'] = int(code)

    def SetData(self, data):
        self.__DATA = data

    # 导出最终结果
    def DumpResult(self):
        # 如果返回为空
        if self.__RET['retcode'] == 200 and self.__DATA is None:
            raise Exception('none of data')

        self.__RET['data'] = self.__DATA

        return self.__RET


class __Controller__(metaclass=Common.__Singleton__):
    """控制器"""

    def __init__(self):
        # 引入模块目录
        self.apiPath = Common.ExtendPath(Config.GetSysSetting('AppSettings', 'api_path'))

        # 得到所有模块配置
        self.mods = Config.GetAllModule()

    def Router(self, type, ver, mod, func, acctoken, seckey, ip, data=None):
        mdata = None
        token = None

        # 截取接口信息
        info = Config.GetRouterByName(ver, mod, func)
        ret = __SerializeData__()

        while True:
            # 找不到接口
            if info is None:
                ret.SetRetCode(404, 'Not Found', 'The API could not be found in st system')
                break

            # 没有设置 SECKEY
            if info['encrypt'] == 'true' and len(seckey) == 0:
                ret.SetRetCode(401, 'Unauthorized', 'No SecretKey was found')
                break

            # 初始化数据
            try:
                agent = Agent.__Agent__(info['resultype'], mod, func, ip)
                if info['datatype'] != '':
                    mdata = Model.__ModelData__(info['datatype'])
            except Exception as e:
                Log.error('initialize data failed', Exception, e)
                ret.SetRetCode(400, 'Bad Request', 'Deserialization parameter failed')
                break

            # 认证身份
            if info['auth'] == 'true':
                # 如果需要验证身份而没有 Token
                if len(acctoken) == 0 or len(seckey) == 0:
                    ret.SetRetCode(401, 'Unauthorized', 'No AccessToken was found')
                    break

                # 解析 Token
                try:
                    token = Auth.__Token__(ver, seckey)
                    token.CheckoutToken(acctoken)
                except Exception as e:
                    Log.error('check out token error', Exception, e)
                    ret.SetRetCode(401, 'Unauthorized', 'AccessToken deserialization failed')
                    break

                # 认证 Token
                try:
                    ifauth = Auth.__Auth__(ver).Auth(agent, ver, mod, func, seckey, token)
                except Exception as e:
                    Log.error('auth handler error', Exception, e)
                    ret.SetRetCode(401, 'Unauthorized', 'Identity authentication error')
                    break

                if not ifauth:
                    ret.SetRetCode(403, 'Forbidden', 'Failed of Identity Authentication')
                    break

            # 解析数据
            try:
                if data is not None and info['datatype'] != '':
                    data = json.loads(data)
                    mdata.CheckoutData(data)
            except Exception as e:
                Log.error('decode data failed', Exception, e)
                ret.SetRetCode(400, 'Bad Request', 'Parameter are incorrect or do not match the API')
                break

            # 装载模块
            try:
                sys.path.append(self.apiPath + '/' + ver)
                newmod = __import__(mod)
                sys.path.pop()
            except Exception as e:
                Log.error('load module error', Exception, e)
                ret.SetRetCode(500, 'Internal Server Error', 'Failed to load API module')
                break

            if hasattr(newmod, func):
                newfunc = getattr(newmod, func)
                try:
                    # 实例化 Handler
                    handler = newfunc()
                    # 将请求交给模块
                    if type == 'GET':
                        handler.get(agent, data, token, seckey)
                    if type == 'POST':
                        handler.post(agent, data, token, seckey)
                except Exception as e:
                    Log.error('handler error', Exception, e)
                    ret.SetRetCode(500, 'Internal Server Error', 'API execution failed')
                    break
            else:
                ret.SetRetCode(503, 'Service Unavailable', 'No module found')
                break

            try:
                ret.SetApiCode(agent.GetApiCode())
                ret.SetData(agent.GetResult())
            except Exception as e:
                Log.error('set response data failed', Exception, e)
                ret.SetRetCode(500, 'Internal Server Error', 'Failed to process returned data')

            break

        try:
            retdata = ret.DumpResult()
        except Exception as e:
            Log.error('set response data failed', Exception, e)
            ret.SetRetCode(202, 'Accepted', 'Request accepted but not processed')
            retdata = ret.DumpResult()

        return retdata, ret.GetHttpCode(), ret.GetHttpReason()


def Router(type, ver, mod, func, acctoken, seckey, ip, data=None):
    C = __Controller__()
    data, httpCode, httpReason = C.Router(type, ver, mod, func, acctoken, seckey, ip, data)

    return data, httpCode, httpReason
