#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 15:29
# @Author  : luoyuediwu
# @Site    : 
# @File    : last_value.py
# @Software: PyCharm
import os
import json
import time
from oslo_log import log
from flask_restful import Resource
from servers_monitor.db.redis_operate import *



from common.restful.restful_utils import RestfulUtilsMixin

__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)

class LastController(Resource, RestfulUtilsMixin):

    def get(self):
        return self.rest_execute_action('get')

    def post(self):
        return self.rest_execute_action('post')

    def _get_snapvalue(self, ids):
        ret = {}
        key_value = []
        ids = {"resources": [{"resources_id": "ip_0"}, {"resources_id": "ip_1"}]}
        try:
            if isinstance(ids, dict):
                _ids = ids.values()[0]
            else:
                _ids = ids
            t = int(time.time())

            for item in _ids:
                if not item.values()[0]:
                    continue
                ret.append(item["resources_id"])
            RedisOpert = RedisOperate()
            key_value = RedisOpert.get_values(ret)
            ret["data"] = key_value
        except Exception as err:
            raise err
        return ret

    def _get_naked(self):
        args = self.load_request_params([self.Param('id', list, True, 'Must specify at least one resource id')])
        try:
            data = self._get_snapvalue([args['id']])
        except Exception as err:
            return self.rest_failed(self.R.EC.OPERATR_FORBID, extra_text='grpc server error: %s' % err)

        return self.rest_success(data=data)

    def _post_naked(self):
        args = self.rest_load_request()
        ids = []
        if self.A.resources in args and isinstance(args[self.A.resources], list):
            for r in args[self.A.resources]:
                if self.A.resource_id in r:
                    ids.append(r[self.A.resource_id])

        if not ids:
            return self.rest_result(self.R.EC.PARAM_EMPTY, extra_text='Must specify at least one resource id')
        try:
            data = self._get_snapvalue(ids)
        except Exception as err:
            return self.rest_failed(self.R.EC.OPERATR_FORBID, extra_text='grpc server error: %s' % err)

        return self.rest_success(data=data)