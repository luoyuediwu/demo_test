#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 11:28
@Filename : api_app_misc
"""
from . import API_V2

def api_module(api, **kwargs):

    user_api = API_V2 + 'user'


    import app.api.user.login
    api.add_resource(app.api.user.login.UserLoginController, user_api + '/login')

