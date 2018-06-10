#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 10:59
# @Author  : luoyuediwu
# @Site    : 
# @File    : __init__.py
# @Software: PyCharm

class AuthCacheBackendFactory:

    @staticmethod
    def new():
        from redis.cache_redis import AuthCacheRedis
        return AuthCacheRedis()

