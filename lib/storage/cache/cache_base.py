#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 15:12
# @Author  : luoyuediwu
# @Site    : 
# @File    : cache_base.py
# @Software: PyCharm


class AuthCacheBase():
    """
    
    """

    def __init__(self):
        pass

    def user_for_session(self,session_id,**kwargs):
        """
        从当前 Session 查找用户ID
        :param session_id: Session ID，与当前缓存存储方式一致
        :return: 用户名
        """
        raise  NotImplemented()

    @staticmethod
    def key_session_cache(session_id):
        return AuthCacheBase.key_for_user(session_id, 'session-cached')

    @staticmethod
    def key_for_user(user_id, tag):
        """
        为用户的缓存创建键名称
        :param user_id: 用户名称或ID
        :param tag:     用户后缀
        :return: 键名称
        """
        return 'auth-cache:%s:%s' % (tag, str(user_id))

    @staticmethod
    def key_resource(account):
        return AuthCacheBase.key_for_user(account, 'resources')

    @staticmethod
    def key_is_admin(account):
        return AuthCacheBase.key_for_user(account, 'isadmin')

    @staticmethod
    def key_user_cache(account):
        return AuthCacheBase.key_for_user(account, 'user-cached')

    @staticmethod
    def key_location(account):
        return AuthCacheBase.key_for_user(account, 'location')

    @staticmethod
    def key_operation(account):
        return AuthCacheBase.key_for_user(account, 'operations')