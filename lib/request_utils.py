#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 10:11
# @Author  : luoyuediwu
# @Site    : 
# @File    : request_utils.py
# @Software: PyCharm

import re
from flask import request
from ..lib.SessionCrypt import SessionCrypt

JSESSIONID = 'JSESSIONID'
X_TEST_SID = 'X_TEST_SID'
JSESSIONID_ = JSESSIONID + '_'
session_check_seq = (X_TEST_SID,JSESSIONID)
session_re = re.compile('[a-fA-F0-9]{32}')
CRYPT_SESSON_RE = re.compile(SessionCrypt.PREFIX+ '[A-Z0-9_-]+', re.IGNORECASE)

def request_remote_ip():
    """
    获得请求的ip
    :return: 
    """
    if request.headers.getlist('X-forwarded-For'):
        remote_addr = request.headers.getlist('X-forwarded-For')[0]
    else:
        remote_addr = request.remote_addr
    return str(remote_addr)

def _get_session_id():
    """
    获得session_id
    :return: 
    """
    for s in session_check_seq:
        get_session_id = request.args.get(s,'')
        if get_session_id:
            return get_session_id
    for s in session_check_seq:
        cookie_session_id = request.cookies.get(s)
        if cookie_session_id:
            return cookie_session_id

def request_session():
    session_id = _get_session_id()
    if session_id and (session_id.startswith(JSESSIONID_) or session_re.match(session_id) or CRYPT_SESSON_RE.match(session_id)):
        return str(session_id)
    else:
        return None
