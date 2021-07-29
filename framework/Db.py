#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Db.py
    @Author      : citang
    @Date        : 2021/7/28 4:49 下午
    @Description : description the function of the file
"""
import pymysql
from framework import Config, Common


class __MysqlDB__:

    def __init__(self):
        self.__SETTING_NAME = 'dbSettings'

        # 获取配置信息
        user = Config.GetSysSetting(self.__SETTING_NAME, 'uname')
        host = Config.GetSysSetting(self.__SETTING_NAME, 'host')
        passwd = Config.GetSysSetting(self.__SETTING_NAME, 'passwd')
        dbname = Config.GetSysSetting(self.__SETTING_NAME, 'dbname')
        port = Config.GetSysSetting(self.__SETTING_NAME, 'port')

        # 打开数据库连接
        conn = pymysql.connect(host=host, port=int(port), user=user, passwd=passwd, db=dbname,
                               cursorclass=pymysql.cursors.DictCursor, charset='utf8mb4')

        # 设置交互数据字符集
        cur = conn.cursor()
        cur.execute("SET NAMES utf8mb4")

        conn.commit()

        self.__CONN = conn
        self.__CUR = cur

    def __del__(self):
        cur = self.__CUR
        conn = self.__CONN

        # 关闭数据库
        cur.close()
        conn.commit()
        conn.close()

    # 检查参数有效性
    def __CheckVaild(self, args, params):
        for name in params.keys():
            # 检查缺省参数
            if name in args:
                raise Exception('PARAMETER ' + name + ' UNDEFINE')

            # 检查参数类型
            if not Common.IsType(args[name], params[name]['type']):
                raise Exception('PARAMETER ' + name + ' TYPE UNVAILD')

        return True

    # 格式化 SQL
    def __FormatSQL(self, sql, args):
        fullSql = sql

        for key in args.keys():
            temp = args[key]
            if type(temp) is str:
                temp = self.__Html_Escape(temp)
            # 兼容 py3 新类型 bytes
            if type(args[key]) is bytes:
                args[key] = args.decode(Config.GetSysSetting('AppSettings', 'charset'))

            if type(temp) is list:
                temp = "(" + '"' + '","'.join(temp) + '""' + ")"
                fullKey = '%(' + key + ')%'
                fullSql = fullSql.replace(fullKey, str(temp))
            else:
                fullKey = '%(' + key + ')%'
                fullSql = fullSql.replace(fullKey, str(temp))

        return fullSql

    # html 转义字符
    def __Html_Escape(self, str):
        str = str.replace('&', '&amp;')
        str = str.replace('"', '&quot;')
        str = str.replace('\'', '&apos;')
        str = str.replace('<', '&lt;')
        str = str.replace('>', '&gt;')
        str = str.replace('\\', '&#92;')
        # str = str.replace(' ', '&nbsp;')
        # str = str.replace('/', '&#x2F;')
        return str

    # 执行 SELECT 语句
    def select(self, name, args):
        lst = []

        cur = self.__CUR
        conn = self.__CONN

        # 获取SQL配置
        sql = Config.GetSelectSQLByName(name)
        params = Config.GetSelectParamByName(name)

        # 检查参数
        self.__CheckVaild(args, params)

        # 格式化参数
        sql = self.__FormatSQL(sql, args)

        cur.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            # 兼容 py3，将多有 bytes 转为 string
            for col in row:
                if type(row[col]) == bytes:
                    row[col] = row[col].decode(Config.GetSysSetting('AppSettings', 'charset'))
            lst.append(row)

        return lst

    def insert(self, name, args):
        cur = self.__CUR
        conn = self.__CONN

        # 获取SQL配置
        sql = Config.GetInsertSQLByName(name)
        params = Config.GetInsertParamByName(name)

        # 检查参数
        self.__CheckVaild(args, params)

        # 格式化参数
        sql = self.__FormatSQL(sql, args)

        ret = cur.execute(sql)
        conn.commit()

        return ret

    def update(self, name, args):
        cur = self.__CUR
        conn = self.__CONN

        # 获取SQL配置
        sql = Config.GetUpdateSQLByName(name)
        params = Config.GetUpdateParamByName(name)

        # 检查参数
        self.__CheckVaild(args, params)

        # 格式化参数
        sql = self.__FormatSQL(sql, args)

        ret = cur.execute(sql)
        conn.commit()

        return ret

    def delete(self, name, args):
        cur = self.__CUR
        conn = self.__CONN

        # 获取SQL配置
        sql = Config.GetDeleteSQLByName(name)
        params = Config.GetDeleteParamByName(name)

        # 检查参数
        self.__CheckVaild(args, params)

        # 格式化参数
        sql = self.__FormatSQL(sql, args)

        ret = cur.execute(sql)
        conn.commit()

        return ret
