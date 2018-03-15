#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import web

urls = (
    '/wx', 'Handle',
)
#app_root = os.path.dirname(_file_)
#temples_root = os.path.join(app_root,'templates')
#render = web.template.render(temples_root)

if __name__ == '__main__':
    app = web.application(urls, globals())
    app.run()
