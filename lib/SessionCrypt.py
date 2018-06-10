#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 10:42
# @Author  : luoyuediwu
# @Site    : 
# @File    : SessionCrypt.py
# @Software: PyCharm

from Crypto.Hash import SHA
from Crypto.Cipher import AES
import time
import binascii
import base64
import struct
class SessionCrypt(object):
    MODE_ENCRYPT = 0
    MODE_DECRYPT = 1
    KEY_SEED = 'XBROTHER SESSION CRYPT KEY'
    PREFIX = 'XSS_'
    SUCCEED = 'SUCCEED'

    class F:
        uid = 'uid'
        account = 'account'
        password = 'password'
        admin_level = 'admin_level'
        creation_time = 'creation_time'
        expire = 'expire'
        session = 'session'
        error = 'error'
        iv = 'iv'

    def __init__(self, seed, mode, **kwargs):
        """
        初始化类，并根据参数自动加密或解密
        :param seed: 密钥种子，不能省略，一般设置为客户端IP地址，加密和解密时，必须使用同一个种子否则解密失败
        :param mode: MODE_* 值，根据值决定加密或解密

        当 mode= MODE_ENCRYPT 时，须提供如下参数。
        :keyword uid:           用户ID
        :keyword account:       用户帐号名称
        :keyword password:      用户密码
        :keyword admin_level:   当前用户的管理员级别
        :keyword creation_time: （可选）创建时间戳，若为指定则使用当前时间
        :keyword expire:        （可选）过期时间，以小时为单位。默认为0，表示不过期
        :keyword iv:            （可选）加密扰码字符串，不能少于 16 个字符，若未指定，则使用SEED生成

        当 mode= MODE_DECRYPT 时，需提供如下参数：
        :keyword session:       加密过的 Session
        """
        self._seed = seed
        self._mode = self.MODE_ENCRYPT if mode == self.MODE_ENCRYPT else self.MODE_DECRYPT
        self._iv = kwargs.get(self.F.iv, self.__crypt_iv())
        self._values = {}
        self._cipher = AES.new(self.__crypt_key(), AES.MODE_CFB, self._iv)
        self._session = ''
        if self._mode == self.MODE_ENCRYPT:
            try:
                self._values = {self.F.uid: int(kwargs[self.F.uid]),
                                self.F.account: kwargs.get(self.F.account, ''),
                                self.F.password: kwargs.get(self.F.password, ''),
                                self.F.admin_level: int(kwargs.get(self.F.admin_level, 30)),
                                self.F.creation_time: int(
                                    kwargs.get(self.F.creation_time, time.mktime(time.localtime()))),
                                self.F.expire: float(kwargs.get(self.F.expire, 0))}
                self._session = self.__encrypt()
            except KeyError:
                self.__set_error_msg("Lost parameter 'uid', 'account' or 'password'")
            except ValueError:
                self.__set_error_msg('Invalid parameter format')

        else:
            self._session = kwargs.get(self.F.session, '')
            values = self.__decrypt()
            self._values = values if values else self._values


    def __crypt_iv(self):
        sha = SHA.new()
        for r in range(0, 10):
            sha.update(self._seed or 'DUMMY')
        return sha.hexdigest()[0:AES.key_size[0]]

    def __crypt_key(self):
        sha = SHA.new()
        sha.update(self.KEY_SEED)
        sha.update(self._seed or 'DUMMY')
        return sha.hexdigest()[0:AES.key_size[0]]

    def __encrypt(self):
        msg = str('%(uid)s|%(account)s|%(password)s|%(admin_level)d|%(creation_time)d|%(expire).2f' % self._values)
        crc = binascii.crc32(msg)
        full_msg = struct.pack('i', crc) + msg
        encrypted_msg = self._cipher.encrypt(full_msg)
        self.__set_error_msg()
        return self.PREFIX + base64.urlsafe_b64encode(encrypted_msg).rstrip('\n=')

    def __set_error_msg(self, msg = SUCCEED):
        self._values[self.F.error] = msg

    @property
    def session(self):
        return self._session

    @property
    def uid(self):
        return self._values[self.F.uid]

    @property
    def account(self):
        if self._values:
            return self._values[self.F.account]
        else:
            return None

    @property
    def password(self):
        return self._values[self.F.password]

    @property
    def admin_level(self):
        return self._values[self.F.admin_level]

    @property
    def user_is_admin(self):
        return self.succeed and self.admin_level <= 10

    @property
    def creation_time(self):
        return self._values[self.F.creation_time]

    @property
    def expire(self):
        return self._values[self.F.expire]

    @property
    def error(self):
        if self._values.get(self.F.error):
            return self._values[self.F.error]
        return self.SUCCEED

    @property
    def succeed(self):
        return self.error == self.SUCCEED