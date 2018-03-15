#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/14 9:26
# @Author  : luoyuediwu
# @Site    : 
# @File    : api_app_pasefile.py
# @Software: PyCharm

from . import API_V2

def api_module(api, **kwargs):

    system_api = API_V2 + 'system'

    import app.api.system.filepase.file_import
    api.add_resource(app.api.system.filepase.file_import.FileImport, system_api + '/file_import')

