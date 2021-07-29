#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : App.py
    @Author      : citang
    @Date        : 2021/7/29 11:09 上午
    @Description : description the function of the file
"""
from data.module import Common


class GetDemo:
    """query"""

    def post(self, agent, data, token, seckey):
        cur = agent.DB()

        params = {'id': data.GetData('id')}
        row = cur.select('getDemoSql', params)

        if len(row) < 1:
            agent.SetApiCode(1)
        else:
            ret = agent.Data('GetDemoRetData')
            ret.SetData('id', row[0]['id'])
            ret.SetData('id', row[0]['id'])
            ret.SetData('id', row[0]['id'])

            agent.SetResult(ret)


class GetPageDemo:
    """page query"""

    def post(self, agent, data, token, seckey):
        cur = agent.DB()

        params = {
            'id': data.GetData('id'),
            'pageIndex': data.GetData('pageIndex'),
            'pageSize': data.GetData('pageSize')
        }

        row = cur.select('getPageDemoSql', params)
        count = cur.select('getPageDemoCountSql', params)

        if len(row) < 1:
            agent.SetApiCode(1)
        else:
            ret = agent.Data('PageRetData')
            ret.AllocList('data')
            for r in row:
                item = {'id': r['id'], 'f1': r['f1'], 'f2': r['f2']}
                ret.AppendList('data', item)
            ret.SetData('count', count[0]['num'])

            agent.SetResult(ret)
