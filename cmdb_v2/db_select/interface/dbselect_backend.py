#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
class DatabaseBackend(object):

    class V:
        """
        版本号标识符
        """
        CI_VERSION = 'ci'

    def __init__(self, params=None):
        self.params = params

    def name(self):
        raise NotImplementedError()