#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
from dbselect_backend import DatabaseBackend

class DatabaseBackendInternal(DatabaseBackend):

    # ------------------------------------------------------------------------------------------------------------------
    # 无关权限的
    def global_init(self):
        raise NotImplementedError()

    def name(self):
        raise NotImplementedError()

    def _load_misc(self, items):
        raise NotImplementedError()

    def _dump_misc(self):
        raise NotImplementedError()

    def _dump_relations(self):
        raise NotImplementedError()

    def new_version_for(self, category, count=1):
        raise NotImplementedError()

    def query_multi_relation(self, params):
        raise NotImplementedError()

    def query_relation(self, params):
        raise NotImplementedError()

    def query_item_count(self,params):
        raise NotImplementedError()
