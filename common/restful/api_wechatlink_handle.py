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

    resources = API_V2 + '/wechat'

    import wechatlink.api.resources.handle
    api.add_resource(wechatlink.api.resources.handle.Handle, resources + '/wx')