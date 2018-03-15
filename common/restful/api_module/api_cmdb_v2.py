#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/13 16:09
# @Author  : luoyuediwu
# @Site    : 
# @File    : api_cmdb_v2.py
# @Software: PyCharm
from . import API_V2 ,CMDB

def api_module(api, **kwargs):

    resources = API_V2 + CMDB + '/resources'

    import cmdb_v2.api.resources.resources
    import cmdb_v2.api.resources.new_id
    import cmdb_v2.api.resources.items
    import cmdb_v2.api.resources.relations
    api.add_resource(cmdb_v2.api.resources.new_id.NewIDController, resources + '/new_id')
    api.add_resource(cmdb_v2.api.resources.resources.ResourceController, resources)
    api.add_resource(cmdb_v2.api.resources.items.ItemController, resources + '/items')
    api.add_resource(cmdb_v2.api.resources.relations.RelationsController, resources + '/relations')