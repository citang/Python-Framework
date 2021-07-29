#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Config.py
    @Author      : citang
    @Date        : 2021/7/28 2:01 下午
    @Description : description the function of the file
"""
import copy
from xml.dom.minidom import parse
import xml.dom.minidom

from framework import Common


class __ParserConfig__(metaclass=Common.__Singleton__):
    """
    解析 DATA/CONFIG 目录中的 SYSCONFIG.XML 文件，
    将该 XML 格式化为字典，存放在单例成员对象中。
    """

    def __init__(self):
        self.__CONFIG_FILE = "sysconfig.xml"
        self.__CONFIG_MAP = {}

        # 唯一创建实例时初始化配置
        self.__Parser()

    def __Parser(self):

        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('configuration')

        # 遍历配置并读取和存储内容
        for config in configs:
            itemList = config.getElementsByTagName('add')
            for item in itemList:

                node = item.parentNode.nodeName
                key = _getAttribute(item, 'key')
                value = _getAttribute(item, 'value')

                if node in self.__CONFIG_MAP:
                    self.__CONFIG_MAP[node][key] = value
                else:
                    self.__CONFIG_MAP[node] = {}
                    self.__CONFIG_MAP[node][key] = value

    def GetSetting(self, group, key):
        ret = None
        while True:

            if group not in self.__CONFIG_MAP:
                break

            if key not in self.__CONFIG_MAP[group]:
                break

            ret = copy.copy(self.__CONFIG_MAP[group][key])
            break

        return ret


class __ParserRouter__(metaclass=Common.__Singleton__):
    """
    解析模块关系配置，存储在 DATA/CONFIG 下的 ROUTER.XML 文件当中，
    模块关系对应路由关系，每个配置都对应响应的模块文件，数据模型和对象
    """

    def __init__(self):
        self.__CONFIG_FILE = 'router.xml'
        self.__CONFIG_MAP = {}

        # 创建实例时初始化配置
        self.__Parser()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('configuration')[0]
        # 遍历配置并读取和存储内容
        itemList = configs.getElementsByTagName('add')
        for item in itemList:
            module = _getAttribute(item, 'module')
            handler = _getAttribute(item, 'handler')
            auth = _getAttribute(item, 'auth')
            encrypt = _getAttribute(item, 'encrypt')
            ver = _getAttribute(item, 'version')

            datatype = _getAttribute(item, 'datatype')
            resultype = _getAttribute(item, 'resultype')

            if ver not in self.__CONFIG_MAP:
                self.__CONFIG_MAP[ver] = {}

            if module not in self.__CONFIG_MAP[ver]:
                self.__CONFIG_MAP[ver][module][handler] = {}

            self.__CONFIG_MAP[ver][module][handler]['version'] = ver
            self.__CONFIG_MAP[ver][module][handler]['auth'] = auth
            self.__CONFIG_MAP[ver][module][handler]['encrypt'] = encrypt
            self.__CONFIG_MAP[ver][module][handler]['datatype'] = datatype
            self.__CONFIG_MAP[ver][module][handler]['resultype'] = resultype

    def GetModuleByName(self, ver, module):

        if ver in self.__CONFIG_MAP:
            if module in self.__CONFIG_MAP[ver]:
                return copy.copy(self.__CONFIG_MAP[ver][module])
            else:
                return None
        else:
            return None

    def GetRouterByName(self, ver, module, handler):

        ret = None
        while True:

            if ver not in self.__CONFIG_MAP:
                break
            if module not in self.__CONFIG_MAP[ver]:
                break
            if handler not in self.__CONFIG_MAP[ver][module]:
                break

            ret = copy.copy(self.__CONFIG_MAP[ver][module][handler])
            break
        return ret

    def GetAllModule(self):
        return copy.copy(self.__CONFIG_MAP)


class __ParserModel__(metaclass=Common.__Singleton__):
    """
    解析数据模型配置文件，每个模型都将杯格式化为对象，
    模块和框架数据交互只能通过数据模型对象
    """

    def __init__(self):
        self.__CONFIG_FILE = 'model.xml'
        self.__CONFIG_MAP = {}

        self.__Parser()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('models')[0]
        itmeList = configs.getElementsByTagName('add')

        for item in itmeList:
            # 根据数据模型名称建立和参数的对应关系
            modelName = _getAttribute(item, 'name')
            params = item.getElementsByTagName('parameter')
            pdic = {}
            for param in params:
                pname = _getAttribute(param, 'name')
                pdic[pname] = {}
                pdic[pname]['type'] = _getAttribute(param, 'type')
                pdic[pname]['value'] = _getAttribute(param, 'value')
                pdic[pname]['isempty'] = _getAttribute(param, 'isempty')
                pdic[pname]['extype'] = _getAttribute(param, 'extype')
                pdic[pname]['description'] = _getAttribute(param, 'description')

            self.__CONFIG_MAP[modelName] = pdic

    def GetModelByName(self, name):

        if name in self.__CONFIG_MAP:
            return copy.copy(self.__CONFIG_MAP[name])
        else:
            return None

    def HasModel(self, name):
        return name in self.__CONFIG_MAP


class __ParserSQL__(metaclass=Common.__Singleton__):
    """
    解析数据库IO配置，分四类，每个SQL语句为单位，每个参数需要检查数据类型
    """

    def __init__(self):
        self.__CONFIG_FILE = 'sql.xml'
        self.__CONFIG_SELECT_MAP = {}
        self.__CONFIG_UPDATE_MAP = {}
        self.__CONFIG_INSERT_MAP = {}
        self.__CONFIG_DELETE_MAP = {}

        self.__Parser()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('sqls')[0]

        selects = configs.getElementsByTagName('select')[0]
        selects = selects.getElementsByTagName('add')

        # 获取所有 select 语句
        for item in selects:
            name = _getAttribute(item, 'name')
            content = _getAttribute(item, 'content')
            description = _getAttribute(item, 'description')

            params = item.getElementsByTagName('parameter')

            pdic = {}
            for param in params:
                pname = _getAttribute(param, 'name')
                pdic[pname] = {}
                pdic[pname]['type'] = _getAttribute(param, 'type')
                pdic[pname]['value'] = _getAttribute(param, 'value')

            self.__CONFIG_SELECT_MAP[name] = {}
            self.__CONFIG_SELECT_MAP[name]['content'] = content
            self.__CONFIG_SELECT_MAP[name]['params'] = pdic
            self.__CONFIG_SELECT_MAP[name]['description'] = description

        updates = configs.getElementsByTagName('update')[0]
        updates = updates.getElementsByTagName('add')

        # 获取所有 UPDATE 语句
        for item in updates:
            name = _getAttribute(item, 'name')
            content = _getAttribute(item, 'content')
            description = _getAttribute(item, 'description')

            params = item.getElementsByTagName('parameter')

            pdic = {}
            for param in params:
                pname = _getAttribute(param, 'name')
                pdic[pname] = {}
                pdic[pname]['type'] = _getAttribute(param, 'type')
                pdic[pname]['value'] = _getAttribute(param, 'value')

            self.__CONFIG_UPDATE_MAP[name] = {}
            self.__CONFIG_UPDATE_MAP[name]['content'] = content
            self.__CONFIG_UPDATE_MAP[name]['params'] = pdic
            self.__CONFIG_UPDATE_MAP[name]['description'] = description

        inserts = configs.getElementsByTagName('insert')[0]
        inserts = inserts.getElementsByTagName('add')

        # 获取所有 INSERT 语句
        for item in inserts:
            name = _getAttribute(item, 'name')
            content = _getAttribute(item, 'content')
            description = _getAttribute(item, 'description')

            params = item.getElementsByTagName('parameter')

            pdic = {}
            for param in params:
                pname = _getAttribute(param, 'name')
                pdic[pname] = {}
                pdic[pname]['type'] = _getAttribute(param, 'type')
                pdic[pname]['value'] = _getAttribute(param, 'value')

            self.__CONFIG_INSERT_MAP[name] = {}
            self.__CONFIG_INSERT_MAP[name]['content'] = content
            self.__CONFIG_INSERT_MAP[name]['params'] = pdic
            self.__CONFIG_INSERT_MAP[name]['description'] = description

        deletes = configs.getElementsByTagName('delete')[0]
        deletes = deletes.getElementsByTagName('add')

        # 获取所有 DELETE 语句
        for item in deletes:
            name = _getAttribute(item, 'name')
            content = _getAttribute(item, 'content')
            description = _getAttribute(item, 'description')

            params = item.getElementsByTagName('parameter')

            pdic = {}
            for param in params:
                pname = _getAttribute(param, 'name')
                pdic[pname] = {}
                pdic[pname]['type'] = _getAttribute(param, 'type')
                pdic[pname]['value'] = _getAttribute(param, 'value')

            self.__CONFIG_DELETE_MAP[name] = {}
            self.__CONFIG_DELETE_MAP[name]['content'] = content
            self.__CONFIG_DELETE_MAP[name]['params'] = pdic
            self.__CONFIG_DELETE_MAP[name]['description'] = description

    def GetSelectSQLByName(self, name):
        """获取 SELECT 配置 SQL 语句"""
        if name in self.__CONFIG_SELECT_MAP:
            return copy.copy(self.__CONFIG_SELECT_MAP[name]['content'])
        else:
            return None

    def GetSelectParamByName(self, name):
        """获取 SELECT 配置 SQL 参数"""
        if name in self.__CONFIG_SELECT_MAP:
            return copy.copy(self.__CONFIG_SELECT_MAP[name]['params'])
        else:
            return None

    def GetInsertSQLByName(self, name):
        if name in self.__CONFIG_INSERT_MAP:
            return copy.copy(self.__CONFIG_INSERT_MAP[name]['content'])
        else:
            return None

    def GetInsertParamByName(self, name):
        if name in self.__CONFIG_INSERT_MAP:
            return copy.copy(self.__CONFIG_INSERT_MAP[name]['params'])
        else:
            return None

    def GetUpdateSQLByName(self, name):
        if name in self.__CONFIG_UPDATE_MAP:
            return copy.copy(self.__CONFIG_UPDATE_MAP[name]['content'])
        else:
            return None

    def GetUpdateParamByName(self, name):
        if name in self.__CONFIG_UPDATE_MAP:
            return copy.copy(self.__CONFIG_UPDATE_MAP[name]['params'])
        else:
            return None

    def GetDeleteSQLByName(self, name):
        if name in self.__CONFIG_DELETE_MAP:
            return copy.copy(self.__CONFIG_DELETE_MAP[name]['content'])
        else:
            return None

    def GetDeleteParamByName(self, name):
        if name in self.__CONFIG_DELETE_MAP:
            return copy.copy(self.__CONFIG_DELETE_MAP[name]['params'])
        else:
            return None


class __ParserAppConfig__(metaclass=Common.__Singleton__):
    """
    解析 DATA/CONFIG 目录中的 APPCONFIG.XML 文件，
    将该 XML 格式化为字典，存放在单例对象成员中。
    """

    def __init__(self):
        self.__CONFIG_FILE = 'appconfig.xml'
        self.__CONFIG_MAP = {}

        self.__Parser()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        configs = root.getElementsByTagName('configuration')

        # 遍历配置并读取和存储内容
        for config in configs:
            itemList = config.getElementsByTagName('add')
            for item in itemList:
                node = item.parentNode.nodeName
                key = _getAttribute(item, 'key')
                value = _getAttribute(item, 'value')

                if node in self.__CONFIG_MAP:
                    self.__CONFIG_MAP[node][key] = value
                else:
                    self.__CONFIG_MAP[node] = {}
                    self.__CONFIG_MAP[node][key] = value

    def GetSetting(self, group, key):
        ret = None
        while True:
            if group not in self.__CONFIG_MAP:
                break
            if key not in self.__CONFIG_MAP[group]:
                break
            ret = copy.copy(self.__CONFIG_MAP[group][key])
            break
        return ret


class __ParserCode__(metaclass=Common.__Singleton__):
    """解析 DATA/CONFIG 目录中的 ERROR.XML 文件"""

    def __init__(self):
        self.__CONFIG_FILE = 'error.xml'
        self.__CONFIG_MAP = {}

        self.__Parser()

    def __Parser(self):
        fullPath = Common.GetConfigPath() + self.__CONFIG_FILE

        # 使用minidom解析器打开 XML 文档
        DOMTree = xml.dom.minidom.parse(fullPath)
        root = DOMTree.documentElement

        # 在集合中获取所有配置
        retCodes = root.getElementsByTagName('retcode')[0]

        # 遍历配置并读取 RETCODE 内容
        itemList = retCodes.getElementsByTagName('add')
        for item in itemList:
            node = item.parentNode.nodeName
            key = _getAttribute(item, 'name')
            value = _getAttribute(item, 'value')

            if node in self.__CONFIG_MAP:
                self.__CONFIG_MAP[node][key] = value
            else:
                self.__CONFIG_MAP[node] = {}
                self.__CONFIG_MAP[node][key] = value

        # 在集合中获取所有配置
        apiCodes = root.getElementsByTagName('apicode')[0]
        itemList = apiCodes.getElementsByTagName('add')
        for item in itemList:
            node = item.parentNode.nodeName
            key = _getAttribute(item, 'name')
            value = _getAttribute(item, 'value')

            if node in self.__CONFIG_MAP:
                self.__CONFIG_MAP[node][key] = value
            else:
                self.__CONFIG_MAP[node] = {}
                self.__CONFIG_MAP[node][key] = value

    def GetCodeById(self, c_type, c_id):
        """根据ID读取代码说明"""
        ret = None
        while True:
            if c_type not in self.__CONFIG_MAP:
                break
            if c_id not in self.__CONFIG_MAP[c_type]:
                break
            ret = copy.copy(self.__CONFIG_MAP[c_type][c_id])
            break
        return ret


def GetRouterByName(version, module, handler):
    """获取模块对应的 Handler 信息"""
    PR = __ParserRouter__()
    return PR.GetRouterByName(version, module, handler)


def GetAllModule():
    """获取所有模块信息"""
    PR = __ParserRouter__()
    return PR.GetAllModule()


def GetModuleByName(name):
    """依据名称获取数据类型"""
    PM = __ParserModel__()
    return PM.GetModelByName(name)


def GetSelectSQLByName(name):
    """获取 SELECT 配置 SQL 语句"""
    PS = __ParserSQL__()
    return PS.GetSelectSQLByName(name)


def GetSelectParamByName(name):
    """获取 SELECT 配置 SQL 参数"""
    PS = __ParserSQL__()
    return PS.GetSelectParamByName(name)


def GetInsertSQLByName(name):
    """获取 Insert 配置 SQL 语句"""
    PS = __ParserSQL__()
    return PS.GetInsertSQLByName(name)


def GetInsertParamByName(name):
    """获取 Insert 配置 SQL 参数"""
    PS = __ParserSQL__()
    return PS.GetInsertParamByName(name)


def GetUpdateSQLByName(name):
    """获取 Update 配置 SQL 语句"""
    PS = __ParserSQL__()
    return PS.GetUpdateSQLByName(name)


def GetUpdateParamByName(name):
    """获取 Update 配置 SQL 参数"""
    PS = __ParserSQL__()
    return PS.GetUpdateParamByName(name)


def GetDeleteSQLByName(name):
    """获取 Delete 配置 SQL 语句"""
    PS = __ParserSQL__()
    return PS.GetDeleteSQLByName(name)


def GetDeleteParamByName(name):
    """获取 Delete 配置 SQL 参数"""
    PS = __ParserSQL__()
    return PS.GetDeleteParamByName(name)


def GetSysSetting(group, key):
    """获取应用程序配置"""
    PC = __ParserConfig__()
    return PC.GetSetting(group, key)


def GetAppConfig(group, key):
    """"""
    PC = __ParserAppConfig__()
    return PC.GetSetting(group, key)


def GetCodeById(c_type, c_id):
    """依据名称获取数据类型"""
    PC = __ParserCode__()
    return PC.GetCodeById(c_type, c_id)


def _getAttribute(obj, name):
    """重写获取属性方法，转换字符集"""
    return Common.TransStr(obj.getAttribute(name), 'utf8')
