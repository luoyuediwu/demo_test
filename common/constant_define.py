#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 18:33
@Filename : constant_define
"""

import os
import sys

class DictParam:
    # 用户、认证相关字段
    user = 'account'
    password = 'password'
    info = 'info'
    account = 'account'
    session_id = 'session_id'
    approved_resources = 'approved_resources'
    version = 'versions'
    resources = 'resources'
    resource_id = 'resource_id'
    attributes = 'attributes'
    relations = 'relations'
    resource_id1 = 'resource_id1'
    resource_id2 = 'resource_id2'
    relation_code = 'relation_code'
    output_format = 'output_format'
    resource_count = 'resource_count'
    total_count = 'total_count'
    page = 'page'
    where = 'where'
    terms = 'terms'
    field = 'field'
    operator ='operator'
    value = 'value'
    deleted = 'deleted'
    size = 'size'
    number = 'number'
    sorts ='sorts'
    type_ = 'type_'
    output = 'output'
    reverse = 'reverse'
    show_all = 'show_all'
    attribute_name = 'attribute_name'
    attribute_value = 'attribute_value'
    list_ = 'list_'
    object_ = 'object_'



class QueryOperation:
    """
    RESTful API 查询条件枚举
    """
    in_ = u'in'
    notin = u'notin'
    like = u'like'
    lt = u'lt'
    gt = u'gt'
    lte = u'lte'
    gte = u'gte'
    neq = u'neq'
    eq = u'eq'
    # 在特殊场合使用
    regex = u'regex'
    regexp = u'regexp'
    isnull = 'isnull'
    notnull = 'notnull'
    exists = 'exists'
    notexists = 'notexists'
    elemmatch = 'elemmatch'

class Commconstant:
    A = DictParam