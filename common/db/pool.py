#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import re
from eventlet import pools
from eventlet import semaphore

class Pool(pools.Pool):
    """tsdb连接池"""
    def __init__(self, create_method, min_size=0, max_size=2):
        super(Pool, self).__init__(min_size=min_size, max_size=max_size)
        self.create_method = create_method
        self._pool_mutex = semaphore.Semaphore()

    def create(self):
        """
        重载父类方法
        """
        return self.create_method()

    def get(self):
        """
        重载父类方法
        """
        # with self._pool_mutex:
        return super(Pool, self).get()

    def put(self, item):
        """
        重载父类方法
        """
        # with self._pool_mutex:
        return super(Pool, self).put(item)

    def empty(self):
        """
        清空池
        """
        while self.free_items:
            self.get().close()


class ConnectionContext(object):
    """连接上下文"""
    def __init__(self, connection_pool):
        self._session = None
        self._connection_pool = connection_pool

    def __enter__(self):
        self._session = self._connection_pool.get()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._connection_pool.put(self._session)


class SingleMeta(type):
    """单例"""
    def __init__(cls, what, bases=None, dict=None):
        super(SingleMeta, cls).__init__(what, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingleMeta, cls).__call__(*args, **kwargs)
        return cls._instance


def parse_tsdb_uri(db_uri):
    """
    格式化tsdb链接字符串
    @param db_uri: xxx://host:port@user/database
    @return:
    """
    pattern = re.compile(r"""
            (?P<name>[\w\+]+)://
            (?:
                (?P<username>[^:/]*)
                (?::(?P<password>[^/]*))?
            @)?
            (?:
                (?:
                    \[(?P<ipv6host>[^/]+)\] |
                    (?P<ipv4host>[^/:]+)
                )?
                (?::(?P<port>[^/]*))?
            )?
            (?:/(?P<keyspace>.*))?
            """, re.X)

    m = pattern.match(db_uri)
    if m is not None:
        components = m.groupdict()
        return components
    else:
        return {}