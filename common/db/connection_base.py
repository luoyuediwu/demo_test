#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 15:09
# @Author  : luoyuediwu
# @Site    : 
# @File    : connection_base.py
# @Software: PyCharm

import contextlib

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from pool import SingleMeta
from ..uri_utils import *

__all__ = ['ConnectionBase', 'SingleMeta']


class ConnectionBase(object):

    # 基类禁止使用单例模式，请在各自的派生类中实现
    # 在派生类中添加如下行，即可实现针对具体数据库的连接单例模式
    # __metaclass__ = SingleMeta

    def __init__(self, db_uri):
        self.engine = create_engine(db_uri, encoding='utf-8', pool_recycle=True)
        self.db_name = uri_keyspace(db_uri)
        self._Session = sessionmaker(bind=self.engine)


    def get_session(self):
        """
        :return: 单个 Session，使用后必须 close
        :rtype: Session
        """
        return self._Session()

    @contextlib.contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self._Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def raw_query(self, sql_text):
        """
        执行SQL语句并返回结果集
        :param sql_text: SQL语句
        :return: 结果集
        """
        result = self.engine.execute(sql_text)
        query_data = result.fetchall()
        result.close()
        return query_data

    def raw_execute(self, sql_text):
        """
        执行SQL语句，但不返回任何结果
        :param sql_text: SQL语句
        """
        with self.engine.begin() as connection:
            connection.execute(sql_text)

    def scalar(self, sql_text):
        """
        执行SQL语句并返回第一行第一列的值，一般用于获取聚合查询结果
        :param sql_text: 查询语句，一般应为 select count(*) 等
        :return: 查询结果
        """
        return self.engine.scalar(sql_text)
