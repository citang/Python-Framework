#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
    @FileName    : Entry.py
    @Author      : citang
    @Date        : 2021/7/27 5:51 下午
    @Description : description the function of the file
"""

import getopt
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from framework import Common, Service, Config


def Usage():
    print('========================================================================')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                             citang                                   +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('+                                                                      +')
    print('========================================================================')
    print('-d , --data: set data path                                             +')
    print('-m , --mode: set 1(local service mode) or 2(proxy mode)                +')
    print('-p , --port: set reverse proxy server port or local listen port        +')
    print('========================================================================')


if __name__ == '__main__':
    # windows: data_path = os.path.join(os.path.abspath(os.path.dirname(os.getcwd())), 'data\\')
    data_path = '../data/'
    # data_path = ''
    port = 0
    mode = 1

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'd:m:p', ['data=', 'mode=', 'port='])
        for name, value in opts:

            if name in ('-d', '--data'):
                data_path = value

            if name in ('-m', '--mode'):
                mode = int(value)

            if name in ('-p', '--port'):
                port = int(value)

    except:
        Usage()
        exit(0)

    Common.SetDataPath(data_path)

    if port == 0:
        port = int(Config.GetSysSetting('AppSettings', 'listen_port'))

    if mode == 1:
        web = Service.__WebService_Flask__()
        web.run(port)

    else:
        pass
