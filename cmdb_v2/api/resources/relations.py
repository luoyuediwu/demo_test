#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
from flask_restful import Resource
from common.restful.restful_utils import *
from cmdb_v2.db_select import BackendFactory
from cmdb_v2.constant_define import *
from cmdb_v2 import CMDB_CONF

class RelationsController(Resource, RestfulUtilsMixin, CMDBDefineMixin):

    def delete(self):
        """批量删除CI项的关系"""
        return self.rest_execute_action('delete')

    def post(self):

        return self.rest_execute_action('post')

    def get(self):

        return self.rest_execute_action('get')

    def _delete_naked(self):
        getargs = self.load_request_params([self.Param(self.A.id1, str, required=True, help_='Resource id1'), self.Param(self.A.id2, list, help_='Resource id2'), self.Param(self.A.relation_code, str, help_='Relation Code')])
        args = {self.A.id1: getargs.get(self.A.id1),
         self.A.id2: getargs.get(self.A.id2),
         self.A.relation_code: getargs.get(self.A.relation_code)}
        if not args[self.A.id1]:
            raise RestfulError(self.R.EC.INVALID_PARAM_FORMAT, 'id1 is mission', self.R.RC.BAD_REQUEST)
        if not args[self.A.id2] and not args[self.A.relation_code]:
            raise RestfulError(self.R.EC.INVALID_PARAM_FORMAT, 'id2 and relation_code should not both empty!', self.R.RC.BAD_REQUEST)
        backend = BackendFactory.new()
        result = backend.delete_relation(args)
        return self.rest_success(result)

    def _post_naked(self):
        args = self.rest_load_request()
        backend = BackendFactory.new()
        return backend.query_relation_item(args)

    def _get_naked(self):
        getargs = self.load_request_params([self.Param(self.A.resource_id, str, required=True, help_='resource_id required'),
         self.Param(self.A.relation_code, int, required=True, help_='relation_code required and should be be a integer'),
         self.Param(self.A.attribute_name, str),
         self.Param(self.A.attribute_value, str),
         self.Param(self.A.output_format, str),
         self.Param(self.A.sorts, str)])
        args = {self.A.resource_id: getargs[self.A.resource_id],
         self.A.relation_code: getargs[self.A.relation_code],
         self.A.output_format: self.A.list_ if getargs[self.A.output_format] == self.A.list_ else self.A.object_}
        if getargs[self.A.attribute_name] and getargs[self.A.attribute_value]:
            args[self.A.where] = [{self.A.terms: [{self.A.field: getargs[self.A.attribute_name],
                              self.A.operator: u'in',
                              self.A.value: getargs[self.A.attribute_value].split(',')}]}]
        if getargs[self.A.sorts]:
            args[self.A.sorts] = eval(getargs[self.A.sorts])
        backend = BackendFactory.new()
        return backend.query_relation_item(args)

