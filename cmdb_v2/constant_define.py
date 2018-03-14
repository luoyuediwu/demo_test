#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/12 9:53
# @Author  : luoyuediwu
# @Site    : 
# @File    : constant_define.py
# @Software: PyCharm

import os
from common.constant_define import DictParam

class EnumErrorText:
    """
    \xe9\x94\x99\xe8\xaf\xaf\xe4\xbf\xa1\xe6\x81\xaf
    """
    sqlite_conn_error = 'sqlite connect error ,cannot open or create the file cmdb.db'
    resource_count_error = 'resource_count is not corrected'
    relation_count_error = 'relation_count is not corrected'
    param_error = 'request params invalid'
    resource_id_not_exist = 'resources table does not have this relation_id, failed!'
    database_add_error = 'add failed!'
    database_update_error = 'update failed!'
    delete_relation_failed = 'delete relation failed!'
    delete_resource_failed = 'delete resource failed!'
    delete_resource_and_relation_failed = 'delete resource and relation failed!'


class EnumErrorCode:
    """
    \xe9\x94\x99\xe8\xaf\xaf\xe7\xa0\x81
    """
    no_error = '0'
    param_error_code = '10001'
    resource_count_error = '10102'
    relation_count_error = '10103'
    resource_id_not_exist = '10104'
    database_connect_error = '20101'
    database_add_error = '20102'
    database_update_error = '20103'
    delete_relation_failed = '20104'
    delete_resource_failed = '20105'
    delete_resource_and_relation_failed = '20106'


class EnumSuccessText:
    """
    \xe6\x88\x90\xe5\x8a\x9f\xe6\x8f\x90\xe7\xa4\xba\xe4\xbf\xa1\xe6\x81\xaf
    """
    delete_relation_success = 'delete relations successfully'
    delete_resource_and_relation_success = 'delete resources and relations successfully'
    post_success = 'CI resources and CI relations add Successfully!'
    put_success = 'CI resources and CI relations update Successfully!'


class URlParam:
    """
    "URL"\xe5\x8f\x82\xe6\x95\xb0\xe4\xbf\xa1\xe6\x81\xaf
    """
    operator_resources_url = '/api/v1/cmdb/resources'
    delete_relations_url = '/api/v1/cmdb/resources/relations'
    simple_search_url = '/api/v1/cmdb/resources'
    tree_search_url = '/api/v1/cmdb/resources/tree'
    has_relation_url = '/api/v1/cmdb/resources/hasrelation'
    fuzzy_delete_url = '/api/v1/cmdb/resources/fuzzy'
    recursive_delete_url = '/api/v1/cmdb/resources/recursive'
    my_host = '0.0.0.0'
    my_port = 5001
    update_sqlite_file_url = '/api/v1/cmdb/update_file'


class RabbitOperator:
    """
    \xe6\xb6\x88\xe6\x81\xaf\xe8\xae\xa2\xe9\x98\x85\xe4\xbf\xa1\xe6\x81\xaf
    """
    post_topic = 'cmdb.resources.post'
    relation_post_topic = 'cmdb.resources.relations.post'
    put_topic = 'cmdb.resources.put'
    delete_topic = 'cmdb.resources.delete'
    relation_delete_topic = 'cmdb.resources.relations.delete'
    method = 'update_cmdb'
    exchange_name = 'cmdb_exchange'
    version = '1.0'


class MongoParam:
    """
    \xe5\xae\x9a\xe4\xb9\x89sqlite\xe8\xbf\x9e\xe6\x8e\xa5\xe5\x8f\x82\xe6\x95\xb0
    """
    mongo_ip = "127.0.0.1"
    mongo_port = 27017
    mongodb_guest = "gj"
    mongodb_pwd = 'xbrother'
    mongodb_db = 'dcs_cmdb'
    slaveok = True
    back_end = 'mongo'

max_resource_id_length = 64

class CMDBDefineMixin:
    ET = EnumErrorText
    ST = EnumSuccessText
    EC = EnumErrorCode
    A = DictParam
    # CI = ResourceItemDefine