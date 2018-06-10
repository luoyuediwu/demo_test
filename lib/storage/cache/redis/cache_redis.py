#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 15:04
# @Author  : luoyuediwu
# @Site    : 
# @File    : cache_redis.py
# @Software: PyCharm

from ..cache_base import AuthCacheBase
from common.constant_define import *
from DataBase.db.db_connection import get_rtdb_connection
from app.lib.SessionCrypt import *
from app.lib.request_utils import *
import contextlib
from app.lib.constant_define import *
from app.lib.model.user_perms import *
from app.lib.storage.cache.cache_base import *
f_session = 'session'

class AuthCacheRedis(AuthCacheBase, Commconstant):

    def __init__(self):
        super(AuthCacheRedis, self).__init__()
        self._conn = get_rtdb_connection()

    def prepare_user_perms(self, user_perms, ttl=TIME_HALF_HOUR, **kwargs):

        def _prepare_user_perms(redis_session):
            if user_perms.operations:
                redis_session.delete(self.key_operation(user_perms.account))
                redis_session.hmset(self.key_operation(user_perms.account), user_perms.operations)

        session = kwargs.get(f_session)
        if session:
            _prepare_user_perms(session)
        else:
            with self._conn.get_session() as session:
                _prepare_user_perms(session)

    def user_for_session(self,session_id,**kwargs):
        """
        按照某个 SessionID 返回对应的用户
        :param session_id: SESSIONID
        :param kwargs: 可能的参数
        :keyword session: 可供复用的 redis session，若不存在需要自行创建连接
        :return: 用户名，若不存在对应的用户则返回 None 
        """
        crypt = SessionCrypt(request_remote_ip(), SessionCrypt.MODE_DECRYPT, session=session_id)
        with self._db_session(**kwargs) as redis_session:
            account = crypt.account if crypt.succeed else redis_session.get(session_id)
            if account and not redis_session.get(self.key_session_cache(session_id)):
                self.refresh_users([account], TIME_HALF_HOUR, session=redis_session)
                redis_session.set(self.key_session_cache(session_id), '1')
        return account

    @contextlib.contextmanager
    def _db_session(self,**kwargs):
        exists_session = kwargs.get(f_session)
        new_session = None
        if exists_session:
            used_session = exists_session
        else:
            new_session = self._conn.get_session()
            used_session = getattr(new_session, '__enter__')()
        try:
            yield used_session
        finally:
            if new_session:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                getattr(new_session, '__exit__')(exc_type, exc_value, exc_traceback)
        return

    def refresh_users(self, users, ttl = 3600, **kwargs):

        def _refersh_users(redis_session):
            for account in users:
                user_perms = UserPerms(account)
                redis_session.delete(self.key_is_admin(user_perms.account))
                if user_perms.is_admin:
                    redis_session.set(self.key_is_admin(user_perms.account), '1')
                else:
                    self.prepare_user_perms(user_perms, session=session)
                redis_session.set(self.key_user_cache(account), '1')

        session = kwargs.get(f_session)
        if session:
            _refersh_users(session)
        else:
            with self._conn.get_session() as session:
                _refersh_users(session)

        def prepare_user_perms(self, user_perms, ttl=TIME_HALF_HOUR, **kwargs):

            def _prepare_user_perms(redis_session):
                # if user_perms.perms:
                #     redis_session.delete(self.key_resource(user_perms.account))
                #     redis_session.hmset(self.key_resource(user_perms.account), user_perms.perms)
                # if user_perms.mask_location:
                #     redis_session.delete(self.key_location(user_perms.account))
                #     redis_session.rpush(self.key_location(user_perms.account), *user_perms.mask_location)
                if user_perms.operations:
                    redis_session.delete(self.key_operation(user_perms.account))
                    redis_session.hmset(self.key_operation(user_perms.account), user_perms.operations)

            session = kwargs.get(f_session)
            if session:
                _prepare_user_perms(session)
            else:
                with self._conn.get_session() as session:
                    _prepare_user_perms(session)


