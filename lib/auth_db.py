#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 15:24
# @Author  : luoyuediwu
# @Site    : 
# @File    : auth_db.py
# @Software: PyCharm

import hashlib
import binascii
import traceback
from collections import OrderedDict
from sqlalchemy import or_
from DataBase.test_common import TEST_CONF
from common.db.connection_base import *
from model.auth_model import *
from model.auth_model import BaseUserRole, BaseUserDepartment, BaseRoleOperaton
from fields import *
__all__ = ['AuthorityDatabase']

class AuthorityDatabase(ConnectionBase):
    __metaclass__ = SingleMeta
    BUILTIN_FLAG = 10
    HASH_INTERATIONS = 1024
    HASH_SALT = '70f25a7240d84607'
    ROOT_MENU_ID = '{0000002F-0000-0000-C000-000000000046}'
    OWNER_MENU_ID = '{0000002F-0000-0000-C000-000000000047}'

    class DatabaseError:
        """
        \xe4\xb8\x80\xe4\xba\x9b\xe6\x95\xb0\xe6\x8d\xae\xe5\xba\x93\xe9\x94\x99\xe8\xaf\xaf\xe4\xbb\xa3\xe7\xa0\x81
        """
        succeed = 'SUCCEED'
        invalid_id = 'INVALID_ID'
        have_children = 'HAVE_CHILDREN'
        protected = 'PROTECTED'
        field_lost = 'FIELD_LOST'
        password_error = 'PASSWORD_ERROR'

    def __init__(self):
        db_uri = TEST_CONF.authority_database
        super(AuthorityDatabase, self).__init__(db_uri)

    def query_user_role(self, userid):
        result = []
        try:
            with self.session_scope() as session:
                userroles = session.query(BaseUserRole.role_id).filter(BaseUserRole.user_id == userid)
                if userroles:
                    for temp in userroles:
                        result.append(temp[0])

        except Exception as e:
            print 'error:%s' % traceback.format_exc()

        return result

    @staticmethod
    def hash_password(password):
        """
        摘抄自原Java代码，具体可参见：
        app/web/gu/src/com/xbrother/system/login/service/LoginService.java
        app/web/gu/src/com/xbrother/common/util/Digests.java
        """
        m = hashlib.sha1()
        hexsalt = binascii.unhexlify(AuthorityDatabase.HASH_SALT)
        m.update(hexsalt)
        m.update(password)
        result = m.digest()
        for i in range(1, AuthorityDatabase.HASH_INTERATIONS):
            mr = hashlib.sha1()
            mr.update(result)
            result = mr.digest()

    def query_one_user(self, user_id = None, account = None, **kwargs):
        """
        查询单个用户的信息
        :param user_id: 用户ID
        :param account: 用户帐号名称，与用户ID不能同时为空
        :keyword with_password: 查询结果中，附带hash后的密码，默认为 False
        :return: 用户基本信息和部门、角色ID
                {
                    "id": 1,
                    "name": "系统管理员11",
                    "account": "admin",
                    "email": "test@yanfa.com",
                    "phone": "0755-26550266",
                    "fax": "0755-26550266",
                    "mobile": "",
                    "status": 1,
                    "remark": "",
                    "default_user": 10,
                    "user_level": 10
                    "departments": {"3": "研发部", "5": "行政部"},
                    "roles": {"1": "管理员", "3": "坐席主管"},
                }
        """
        if user_id is None and account is None:
            return
        else:
            with_password = kwargs.get('with_password')
            with self.session_scope() as session:
                query = session.query(BaseUsers).filter(BaseUsers.row_status == BaseUsers.ROW_STATUS_USED)
                if user_id:
                    query = query.filter(BaseUsers.id == user_id)
                else:
                    query = query.filter(BaseUsers.account == account)
                user = query.one_or_none()
                if user is None:
                    return
                result = {f_id: user.id,
                 f_name: user.name,
                 f_account: user.account,
                 f_email: user.email,
                 f_phone: user.phone,
                 f_fax: user.fax,
                 f_mobile: user.mobile,
                 f_status: user.status,
                 f_remark: user.remark,
                 f_default_user: user.default_user,
                 f_user_level: user.user_level,
                 f_departments: {str(d.id):d.name for d in user.departments},
                 f_roles: {str(r.id):r.name for r in user.roles}}
                if with_password:
                    result[f_password] = user.password
                return result
            return