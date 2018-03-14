#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/14 10:24
# @Author  : luoyuediwu
# @Site    : 
# @File    : items.py
# @Software: PyCharm

from flask_restful import Resource
from oslo_log import log
from common.restful.restful_utils import *
from cmdb_v2.db_select import BackendFactory
from cmdb_v2.constant_define import *
import os
__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)

class ItemController(Resource, RestfulUtilsMixin):

    def post(self):
        return self.rest_execute_action('post')

    def _post_naked(self):
        args = self.rest_load_request()
        backend = BackendFactory.new()
        return backend.query_item(args)

    def get(self):
        return self.rest_execute_action('get')

    def _get_naked(self):
        args = self.rest_load_request()
        backend = BackendFactory.new()
        return backend.query_item(args)
        # data={"zxw":"dasda"}
        # return self.rest_success({u'new_id': "asdadas"})