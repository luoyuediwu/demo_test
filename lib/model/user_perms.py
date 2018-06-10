#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/29 14:03
# @Author  : luoyuediwu
# @Site    : 
# @File    : user_perms.py
# @Software: PyCharm

from auth_model import BaseUsers, BaseRoles, BaseRoleOperaton, RoleResourcePerms
from ...lib.constant_define import *
from common.constant_define import Commconstant, QueryOperation
from ...lib.auth_db import *
from ..fields import *
NOT_SELECTED = 0
SELECTED = 1
SELECTED_BY_CHILDREN = 2
class UserPerms(Commconstant):
    OP = QueryOperation

    def __init__(self, account):
        self.conn = AuthorityDatabase()
        self.session = self.conn.get_session()
        self.user = None
        self.user_id = 0
        self.account = account
        self.operations = {}
        self.perms = {}
        self.mask_location = None
        self.is_admin = False
        self.__set_user()
        if self.user:
            if self.user.user_level == ADMIN_USER_LEVEL:
                self.is_admin = True
                return
            role_ids = []
            resultrid = self.conn.query_user_role(self.user_id)
            if resultrid:
                for item in resultrid:
                    role_ids.append(item)
            self.__calc_perm()
        return

    def __set_user(self):
        user = self.session.query(BaseUsers).filter(BaseUsers.account == self.account,
                                                    BaseUsers.row_status == BaseUsers.ROW_STATUS_USED).one_or_none()
        if user is None:
            return
        else:
            self.user_id = user.id
            self.user = user
            return

    def __calc_perm(self):
        for role in self.user.roles:
            self.__merge_opeeration(role)

    def __merge_opeeration(self, role):
        """
        :type role: BaseRoles
        """
        for op in role.operations:
            self.operations[op.id] = op.title

