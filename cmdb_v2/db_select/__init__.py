#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/12 10:23
# @Author  : luoyuediwu
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm

from cmdb_v2 import CMDB_CONF
from interface.dbselect_backend_internal import DatabaseBackendInternal
#avaiable_backends = ['mongo', 'sqlite', 'mysql']
avaiable_backends = ['mongo']
class BackendFactory:
    current_backend = None

    @staticmethod
    def new(params = None, custom_backend = None):
        """
        根据配置文件加载当前默认的 CMDB 后端
        :return: CMDB 后端实现类的新实例
        :rtype: CMDBBackendInternal
        """
        if not BackendFactory.current_backend:
            #BackendFactory.current_backend = CMDB_CONF.backend
            BackendFactory.current_backend = "mongo"
        backend = custom_backend if custom_backend is not None else BackendFactory.current_backend
        if backend not in avaiable_backends:
            raise KeyError('invalid cmdb backend "%s", avaiable backends: %r' % (backend, avaiable_backends))
        inst = None
        if backend == 'sqlite':
            import sqlite.cmdb_backend
            inst = sqlite.cmdb_backend.CMDBSqliteBackend(params)
        elif backend == 'mysql':
            import mysql.cmdb_backend
            inst = mysql.cmdb_backend.CMDBMySqlBackend(params)
        elif backend == 'mongo':
            import mongodb.db_select_backend
            inst = mongodb.db_select_backend.CMDBMongoBackend(params)
        if inst is not None:
            inst.global_init()
        return inst