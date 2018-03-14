# 2017.12.13 14:40:22 HKT
#Embedded file name: /opt/build/workspace/KE-V3R2/proj-V3R2C00/gu/cmdb_v2/api/resources/resources.py
from flask_restful import Resource
from oslo_log import log
import grpc
from common.restful.restful_utils import *
from cmdb_v2.constant_define import *
from cmdb_v2 import CMDB_CONF
from common.confs import COMMON_CONF
from cmdb_v2.db_select import BackendFactory
import os
import re
__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)
PORT_FILE_PATH = '/opt/{0}/etc/{0}/port_config_local.json'.format(COMMON_CONF.product)

class ResourceController(Resource, RestfulUtilsMixin, CMDBDefineMixin):

    def get(self):
        """
        \xe6\xa0\xb9\xe6\x8d\xaeresource_id\xe4\xb8\x8erelation_code\xe7\xae\x80\xe5\x8d\x95\xe6\x9f\xa5\xe8\xaf\xa2
        :return: \xe6\xb7\xbb\xe5\x8a\xa0\xe7\xbb\x93\xe6\x9e\x9c\xe5\x92\x8c\xe9\x94\x99\xe8\xaf\xaf\xe4\xbb\xa3\xe7\xa0\x81
        """
        return self.rest_execute_action('get')

    def post(self):
        """
        \xe6\x89\xb9\xe9\x87\x8f\xe6\xb7\xbb\xe5\x8a\xa0CI\xe9\xa1\xb9\xe5\x92\x8c\xe5\x85\xb3\xe7\xb3\xbb
        \xe5\x8f\x82\xe8\xa7\x81\xe6\xa6\x82\xe8\xa6\x81\xe8\xae\xbe\xe8\xae\xa1\xe6\x96\x87\xe6\xa1\xa3\xe7\xab\xa0\xe8\x8a\x82\xe2\x80\x9c3.2.2.1        \xe5\xa2\x9e\xe5\x8a\xa0CI\xe9\xa1\xb9\xe5\x92\x8cCI\xe9\xa1\xb9\xe5\x85\xb3\xe7\xb3\xbb\xe2\x80\x9d
        :return: \xe6\xb7\xbb\xe5\x8a\xa0\xe7\xbb\x93\xe6\x9e\x9c\xe5\x92\x8c\xe9\x94\x99\xe8\xaf\xaf\xe4\xbb\xa3\xe7\xa0\x81
        """
        return self.rest_execute_action('post')

    def put(self):
        """
        \xe6\x89\xb9\xe9\x87\x8f\xe4\xbf\xae\xe6\x94\xb9CI\xe9\xa1\xb9\xe5\x92\x8c\xe5\x85\xb3\xe7\xb3\xbb
        \xe4\xb8\x8e\xe5\xa2\x9e\xe5\x8a\xa0\xe4\xb8\x80\xe6\xa0\xb7\xef\xbc\x8c\xe7\x94\xb1\xe5\x90\x8e\xe7\xab\xaf\xe8\x87\xaa\xe8\xa1\x8c\xe5\x86\xb3\xe5\xae\x9a\xe6\x98\xaf\xe5\xa2\x9e\xe5\x8a\xa0\xe6\x88\x96\xe8\x80\x85\xe6\x9b\xb4\xe6\x96\xb0\xef\xbc\x8c\xe6\x94\xaf\xe6\x8c\x81\xe6\x9b\xb4\xe6\x96\xb0CI\xe9\xa1\xb9\xe7\x9a\x84\xe5\x8d\x95\xe4\xb8\xaa\xe5\xb1\x9e\xe6\x80\xa7(resource_id \xe4\xb8\x8d\xe8\x83\xbd\xe4\xbf\xae\xe6\x94\xb9)
        """
        return self.rest_execute_action('put')

    def delete(self):
        """
        \xe6\x89\xb9\xe9\x87\x8f\xe5\x88\xa0\xe9\x99\xa4CI\xe9\xa1\xb9\xe5\x92\x8c\xe5\x85\xb3\xe7\xb3\xbb
        \xe5\x8f\x82\xe8\xa7\x81\xe6\xa6\x82\xe8\xa6\x81\xe8\xae\xbe\xe8\xae\xa1\xe6\x96\x87\xe6\xa1\xa3\xe7\xab\xa0\xe8\x8a\x82\xe2\x80\x9c3.2.2.2        \xe5\x88\xa0\xe9\x99\xa4CI\xe9\xa1\xb9\xe5\x92\x8cCI\xe9\xa1\xb9\xe5\x85\xb3\xe7\xb3\xbb\xe2\x80\x9d
        :return: \xe6\xb7\xbb\xe5\x8a\xa0\xe7\xbb\x93\xe6\x9e\x9c\xe5\x92\x8c\xe9\x94\x99\xe8\xaf\xaf\xe4\xbb\xa3\xe7\xa0\x81
        """
        return self.rest_execute_action('delete')

    def _get_naked(self):
        getargs = self.load_request_params([self.Param(self.A.resource_id, str, required=True, help_='resource_id required'), self.Param(self.A.relation_code, int, help_='relation_code required and should be be a integer')])
        backend = BackendFactory.new()
        if getargs.get(self.A.relation_code):
            args = {self.A.resource_id: getargs[self.A.resource_id],
             self.A.relation_code: getargs[self.A.relation_code]}
            return backend.query_relation_item(args)
        args = {self.A.deleted: self.A.both,
         self.A.where: [{self.A.terms: [{self.A.field: self.A.resource_id,
                                         self.A.operator: 'in',
                                         self.A.value: getargs[self.A.resource_id].split(',')}]}]}
        return backend.query_item(args)

    def _post_naked(self):
        args = self.rest_load_request()
        backend = BackendFactory.new()
        result = backend.batch_add_ci(args)
        status = 0 if result[0]['error_code'] == '00' else 1
        return self.rest_success()

