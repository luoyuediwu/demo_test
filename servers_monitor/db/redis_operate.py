#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 16:06
# @Author  : luoyuediwu
# @Site    : 
# @File    : redis_operate.py
# @Software: PyCharm


__version__ = '1.0.0.1'
from oslo_log import log
from redis import StrictRedis
import traceback
import json
import time
import os

# __name__ = globals().get('__name__')
# __file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
# LOG = log.getLogger(__name__)
DEFAULT_RTDB_HOST = 'localhost'
DEFAULT_RTDB_PORT = 6379


# class RtdbEngine(object):
#     def get_connection(self, db_uri):
#         return Connection(db_uri)


class RedisOperate():
    def __init__(self):
        # self.username = ""
        # self.password =
        self.address = "127.0.0.1"
        self.port = 6379
        # self.keyspace = url_params.get('keyspace')
        self.operater = self._connect()

    def _connect(self):
        """
        \xe5\x88\x9b\xe5\xbb\xba\xe8\xbf\x9e\xe6\x8e\xa5
        """
        return StrictRedis(self.address, self.port)

    def save_values(self, values):
        _d = {}
        for entity in values:
            device = entity.get('device', None)
            try:
                if device and device.get('resource_id', None) and device.get('status', None) not in ('None', None):
                    _d['SPOTS:%s' % device['resource_id']] = json.dumps(
                        {'save_time': int(float(device.get('timestamp', 0) or device.get('save_time', 0))),
                         'real_value': '%s' % device['status'],
                         'status': int(device['status'])})
            except Exception as err:
                LOG.warn('device error to save rtdb. err: %s data: %s' % (err, device))

            for spot in entity.get('spots', []):
                try:
                    if spot.get('real_value', None) not in ('None', None):
                        _d['SPOTS:%s' % spot['resource_id']] = json.dumps(
                            {'save_time': int(float(spot.get('timestamp', 0) or spot.get('save_time', 0))),
                             'real_value': spot['real_value'],
                             'status': int(spot['status'])})
                except Exception as err:
                    LOG.warn('spot error to save rtdb. err: %s data: %s' % (err, spot))

        if _d:
            with self.get_session() as session:
                session.mset(_d)

    def get_values(self, resources):
        key_value = list()
        if not isinstance(resources, list):
            resources = [resources]
        for res in resources:
            tmp = {}
            tmp[res] = self.operater.get('%s' % res)
            key_value.append(tmp)
        print key_value


