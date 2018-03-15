#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 19:17
@Filename : base
"""

import re

from oslo_db.sqlalchemy import enginefacade
from oslo_config import cfg

class TestBaseConnection(object):
    """数据库连接"""

    # modified by wangzhan @ 2016-06-21 基类禁止使用单例模式，请在各自的派生类中实现
    #__metaclass__ = pool.SingleMeta

    def __init__(self, db_uri, autocommit=True, expire_on_commit=False):
        # NOTE(Alexei_987) Related to bug #1271103
        #                  we steal objects from sqlalchemy_session
        #                  to manage their lifetime on our own.
        #                  This is needed to open several db connections
        self._connection = enginefacade.LegacyEngineFacade(
            sql_connection=db_uri, autocommit=autocommit, expire_on_commit=expire_on_commit,
            _conf=cfg.CONF)

        self.db_name = ''
        m = re.match(r'[^?]+/([^?]+)(\?.*)?$', db_uri)
        if m:
            self.db_name = m.group(1)

    def _get_db_session(self):
        return self._connection.get_session()

    def get_db_session(self):
        """
        暴露 session 给外部接口
        """
        return self._get_db_session()

    def raw_query(self, sql_text):
        """
        执行SQL语句并返回结果集
        :param sql_text: SQL语句
        :return: 结果集
        """
        session = self._get_db_session()
        try:
            session.execute("use %s;" % self.db_name)
            query = session.execute(sql_text)
            query_data = query.fetchall()
            return query_data
        finally:
            session.close()

    def raw_execute(self, sql_text):
        """
        执行SQL语句，但不返回任何结果
        :param sql_text: SQL语句
        """
        session = self._get_db_session()
        try:
            session.execute("use %s;" % self.db_name)
            query = session.execute(sql_text)
        finally:
            session.close()

    def scalar(self, sql_text):
        """
        执行SQL语句并返回第一行第一列的值，一般用于获取聚合查询结果
        :param sql_text: 查询语句，一般应为 select count(*) 等
        :return: 查询结果
        """
        session = self._get_db_session()
        try:
            session.execute("use %s;" % self.db_name)
            return session.scalar(sql_text)
        finally:
            session.close()

    def delete_query(self, resource_id):
        """
        删除历史事件
        :param resource_id:
        :return:
        """
        raise NotImplementedError()

if __name__=="__main__":
    db_uri='mysql://gj:xbrother@localhost/test'
    m = re.match('[^?]+/([^?]+)(\\?.*)?$', db_uri)
    print m.group(2)
    if m:
       db_name = m.group(1)
    print db_name