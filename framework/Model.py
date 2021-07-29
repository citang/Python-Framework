#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Model.py
    @Author      : citang
    @Date        : 2021/7/28 5:22 下午
    @Description : description the function of the file
"""
import copy

from framework import Config, Common


class __ModelData__:

    def __init__(self, modelName):
        # 依据模型名称获取模型结构
        model = Config.GetModelByName(modelName)

        # 若没有找到对应关系则抛出异常
        if model is None:
            raise Exception('not found model : %s' % modelName)

        # 格式化模型
        self.__MODEL = model
        self.__CheckoutData(model)

        # 绑定名称
        self.__MYNAME = modelName

    def __ChechVaild(self, name, data):

        # 数据类型不允许为 None
        if name is None or data is None:
            raise Exception('name or data is none!')

        # 检查是否存在该字段
        if name not in self.__MODEL:
            raise Exception('not found key : %s' % name)

        # 检查类型是否一致
        if not Common.IsType(data, self.__MODEL[name]['type']):
            raise Exception('type error : %s | %s ' % (name, self.__MODEL[name]['type']))

    def __CheckoutData(self, model):

        data = {}
        # 从模型格式化到数据字典
        for key in model.keys():
            value = model[key]['value']
            type = model[key]['type']

            if model[key]['type'] != 'list':
                data[key] = Common.TransType(value, type)

        self.__DATA = data

    def __CheckFinished(self):
        # 按照数据模型校验数据是否符合要求
        model = self.__MODEL

        for key in model.keys():
            isempty = model[key]['isempty']

            if isempty == 'false' and self.__DATA[key] is None:
                raise Exception('must not empty : %s !' % key)

    def CheckoutData(self, data):

        # 检查键数是否相等
        if len(data.keys()) != len(self.__MODEL.keys()):
            raise Exception('data keys not same of model')

        # 检查是否今儿模型内容匹配
        for key in data.keys():
            if key not in self.__MODEL:
                raise Exception('different of data and model')

        # 强制转换类型
        for key in data.keys():

            if self.__MODEL[key]['type'] == 'list':
                pass
            elif self.__MODEL[key]['type'] == 'dict':
                pass
            else:
                data[key] = Common.TransType(data[key], self.__MODEL[key]['type'])

        self.__DATA = data
        self.__CheckFinished()

    def DumpDict(self):
        # 检查是否具备 DUMP 要求
        self.__CheckFinished()
        return copy.copy(self.__DATA)

    def GetName(self):
        return copy.copy(self.__MYNAME)

    def SetData(self, name, data):
        # 检查类型
        self.__ChechVaild(name, data)

        # 检查是否为列表、字典
        if isinstance(type(data), type[1]) or isinstance(type(data), type({1: 1})):
            raise Exception('type not is dict or list')

        self.__DATA[name] = data

    def GetData(self, name):
        if name in self.__DATA:
            return self.__DATA[name]
        else:
            raise Exception('not has key | %s ' % name)

    def AllocList(self, name):
        # 检查类型
        self.__ChechVaild(name, [])
        self.__DATA[name] = []

    def AppendList(self, name, data):
        if data is None:
            raise Exception('data is none')

        # 检查模型格式是否符合要求
        if not Common.IsType(data, self.__MODEL[name]['extype']):
            raise Exception('dat model cant match')

        if self.__DATA[name] is None:
            raise Exception('list not initialize')

        self.__DATA[name].append(data)

    def AppendListEx(self, name, data):

        if data is None:
            raise Exception('data is none')

        # 检查模型格式是否符合要求
        if data.GetName() != self.__MODEL[name]['extype']:
            raise Exception('dat model cant match')

        if self.__DATA[name] is None:
            raise Exception('list not initialize')

        self.__DATA[name] = data.DumpDict()

    def AllocDict(self, name):

        # 检查类型
        self.__ChechVaild(name, {})
        self.__DATA[name] = {}

    def SetDict(self, name, data):
        if data is None:
            raise Exception("data is none")

        # 检查模型格式是否符合要求
        if data.GetName() != self.__MODEL[name]['extype']:
            raise Exception("")

        if self.__DATA[name] is None:
            raise Exception('list not initialize')

        self.__DATA[name] = data.DumpDict()
