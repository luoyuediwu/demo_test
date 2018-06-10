#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 17:40
@Filename : user_operator
"""
import hashlib
import binascii

from oslo_config import cfg
from DataBase.db.rdb.test_database_connection import TESTDatabaseConnection
from common.restful.restful_utils import RestfulUtilsMixin, RestfulError
from common.restful.sql_database_utils import MySqlDatabaseUtilsMinxin
from common.constant_define import Commconstant

class UserOperator(RestfulUtilsMixin, MySqlDatabaseUtilsMinxin,Commconstant):
    HASH_INTERATIONS = 1024
    HASH_SALT = '70f25a7240d84607'

    avaiable_fields = [
        'email',
        'mobile',
        'phone',
        'password',
    ]

    def __init__(self):
        self.conn = TESTDatabaseConnection(autocommit=True, expire_on_commit=False)

    def verify_base_params(self, args):
        print (self.A.user,self.A.password)
        if self.A.user not in args or self.A.password not in args or not args[self.A.user] or not args[self.A.password]:
            raise RestfulError(self.R.EC.PARAM_EMPTY, "user or password should not be empty!", self.R.RC.BAD_REQUEST)

    def verify_user(self, args):
        (user, password, hashpass) = self.__extract_account(args)
        print hashpass
        try:
            result = self.conn.raw_query("select `account`, `password` from itom_base_users where account='%s' limit 1"
                                         % self.addslashes(user))
        except Exception as  e:
            print e
        for row in result:
            if row[0] == user:
                if row[1].lower() == hashpass:
                    return self.rest_success()
                else:
                    raise RestfulError(self.R.EC.UNAUTHORIZED, "Password verify faild for user %s" % user)
        raise RestfulError(self.R.EC.UNAUTHORIZED, "User %s not found" % user)

    def modify_user(self, args):
        """
        更新用户信息，注意此方法不会再校验用户，假设前面已经检查过有效性
        :param args: 要更新的用户信息，数据在 info 字段中
        """
        (user, password, hashpass) = self.__extract_account(args)
        fields = []
        for f in args[self.A.info]:
            if f in self.avaiable_fields:
                if f == self.A.password:
                    args[self.A.info][f] = self.hash_password(args[self.A.info][f])
                fields.append("`{}`='{}'".format(f, self.addslashes(args[self.A.info][f])))
        if not fields:
            return self.rest_result(self.R.EC.PARAM_EMPTY, extra_text="Invalid or empty user info!")

        sql = "update `itom_base_users` set {}".format(', '.join(fields))
        sql += " where `account`='{}' and `password`='{}'".format(user, hashpass)

        session = self.conn.get_db_session()
        session.execute('use %s;' % self.conn.db_name)
        try:
            session.execute(sql)
            return self.rest_success()
        finally:
            session.close()

    def query_user(self, args):
        """
        根据用户名和密码查询用户信息
        :param args: 用户名和密码
        """
        (user, password, hashpass) = self.__extract_account(args)
        filed_keys = ['account', self.A.password] + self.avaiable_fields
        sql = "select `{}` from itom_base_users WHERE `account`='{}' limit 1".format('`, `'.join(filed_keys), user)

        qr = self.conn.raw_query(sql)
        for row in qr:
            result = {}
            for i in range(0, len(filed_keys)):
                result[filed_keys[i]] = row[i]
            result[self.A.user] = result['account']
            del result['account']
            return self.rest_success(data=result)

    def list_user(self):
        """
        列出所有用户
        """
        sql = "select `account`, `user_name`, `user_no`, `email`, `office_tel` as `phone`, `mobile`, `employee_id` from fa_employee" \
              " order by account"
        qr = self.conn.raw_query(sql)
        result = []
        for row in qr:
            result.append({
                'account': row['account'],
                'user_name': row['user_name'],
                'user_no': row['user_no'],
                'email': row['email'],
                'phone': row['phone'],
                'mobile': row['mobile'],
                'employee_id': row['employee_id'],
            })
        return self.rest_success(data={'user': result})

    def __extract_account(self, args):
        return args[self.A.user], args[self.A.password], self.hash_password(args[self.A.password])

    def hash_password(self, password):
        """
        摘抄自原Java代码，具体可参见：
        app/web/test/src/com/xbrother/system/login/service/LoginService.java
        app/web/test/src/com/xbrother/common/util/Digests.java
        """
        m = hashlib.sha1()

        hexsalt = binascii.unhexlify(self.HASH_SALT)
        m.update(hexsalt)
        m.update(password)

        result = m.digest()
        for i in range(1, self.HASH_INTERATIONS):
            mr = hashlib.sha1()
            mr.update(result)
            result = mr.digest()

        return binascii.hexlify(result)


