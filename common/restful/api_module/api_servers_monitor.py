#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
from . import API_V2

def api_module(api, **kwargs):

    system_api = API_V2 + 'server'

    import servers_monitor.api.ip_resources.last_value
    api.add_resource(servers_monitor.api.ip_resources.last_value.LastController, system_api + '/last_value')
