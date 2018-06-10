#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 11:35
@Filename : login
"""

from flask_restful import Resource
from common.restful.restful_utils import *
from .user_operator import UserOperator
from common.constant_define import Commconstant
from app.lib.storage.cache import AuthCacheBackendFactory
from app.lib.request_utils import *
from app.lib.auth_db import *
from app.lib.fields import *
from logagent.log_api import write_oplog

class UserLoginController(Resource, RestfulUtilsMixin,Commconstant):

    def post(self):
        """
        用户登录接口，具体参见设计文档章节“3.3.1.1	用户登录”
        """
        print("post : xzczczczc")
        return self.rest_execute_action('post')

    def _post_naked(self):
        request_ip = request_remote_ip()
        args = self.rest_load_request()
        conn = AuthorityDatabase()
        account = args.get(f_account)
        password = args.get(f_password)
        if not account or not password:
            write_oplog.writelog(user=account,module='系统管理',result=1,args=str(args))
            return self.rest_result(self.R.EC.PARAM_LOST,extra_text='Must specify account and password!')
        else:
            password = conn.hash_password(password)
            user = conn.query_one_user(account=account,with_password=True)
            if user is None:
                write_oplog.writelog(user=account, module='\xe7\xb3\xbb\xe7\xbb\x9f\xe7\xae\xa1\xe7\x90\x86', type=4, ip=request_ip, desc='\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95', result=1, args=str(args))
                return self.rest_failed(self.R.EC.UNAUTHORIZED, extra_text='Account not exist')
            if password != user[f_password]:
                write_oplog.writelog(user=account, module='\xe7\xb3\xbb\xe7\xbb\x9f\xe7\xae\xa1\xe7\x90\x86', type=4, ip=request_ip, desc='\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95', result=1, args=str(args))
                return self.rest_failed(self.R.EC.UNAUTHORIZED)
            session_key = SessionCrypt(request_remote_ip(), SessionCrypt.MODE_ENCRYPT, uid=user[f_id], account=user[f_account], password=password[:4], admin_level=user[f_user_level]).session
            cache = AuthCacheBackendFactory.new()
            cache.refresh_users([account])
            write_oplog.writelog(user=account, module='\xe7\xb3\xbb\xe7\xbb\x9f\xe7\xae\xa1\xe7\x90\x86', type=4,
                                 ip=request_ip, desc='\xe7\x94\xa8\xe6\x88\xb7\xe7\x99\xbb\xe5\xbd\x95', result=0,
                                 args=str(args))
            return self.rest_success(data={f_session: session_key,
             f_id: user[f_id],
             f_account: user[f_account],
             f_name: user[f_name]})


