#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/12 10:37
# @Author  : luoyuediwu
# @Site    : 
# @File    : new_id.py
# @Software: PyCharm

import os
import sys
from flask_restful import Resource, reqparse
from common.restful.restful_utils import *
from cmdb_v2.db_select import BackendFactory

class NewIDController(Resource, RestfulUtilsMixin):

    def get(self):
        """
        获取当前CMDB可用的最新ID
        具体参见设计文档章节“3.3.6  测点ID生成
        """
        return self.rest_execute_action('get')

    def _get_naked(self):
        args = self.load_request_params([self.Param('rule_name', str, True, 'rule_name should not be empty!'), self.Param('count', int)])
        rule_name = args['rule_name']
        count = args.count if args.count and args.count > 1 else 1
        count = count if count <= 1000 else 1000
        backend = BackendFactory.new()
        ids = backend.new_version_for(rule_name, count)
        if not isinstance(ids, list):
            ids = [ids]
        return self.rest_success({u'new_id': ids})

