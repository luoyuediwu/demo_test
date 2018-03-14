#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/12 9:56
# @Author  : luoyuediwu
# @Site    : 
# @File    : rabbit_mq.py
# @Software: PyCharm

from oslo_log import log
from cmdb_v2 import CMDB_CONF
from common.mq.mq_publisher import Publisher
import os

__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)


class SettingPublisher(object):
    """
    \xe5\x8f\x91\xe5\xb8\x83MQ\xe6\xb6\x88\xe6\x81\xaf
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            _mk = super(SettingPublisher, cls)
            cls._instance = _mk.__new__(cls, *args, **kwargs)
            cls._instance.init()
            return cls._instance
        else:
            return cls._instance

    def init(self):
        """
        \xe5\x88\x9d\xe5\xa7\x8b\xe5\x8c\x96\xe8\xae\xa2\xe9\x98\x85\xe6\xb6\x88\xe6\x81\xaf
        :return:
        """
        self._change_client = Publisher(exchange=CMDB_CONF.exchange_name, queue=None, routing_key=CMDB_CONF.post_topic)

    def setting(self, settings, mode, uri, topic):
        """

        :param settings:\xe5\x8f\x91\xe9\x80\x81\xe7\x9a\x84\xe6\x95\xb0\xe6\x8d\xae\xe7\xbb\x93\xe6\x9e\x84
        :param mode:\xe5\xa2\x9e\xe5\x88\xa0\xe6\x94\xb9\xe6\x9f\xa5\xe7\x9a\x84\xe6\x93\x8d\xe4\xbd\x9c\xe7\xb1\xbb\xe5\x9e\x8b
        :param uri:\xe4\xbc\xa0\xe9\x80\x92\xe7\x9a\x84uri
        :param topic:\xe4\xbc\xa0\xe9\x80\x92\xe7\x9a\x84topic
        :return:
        """
        body = {'type': mode,
                'uri': uri,
                'body': settings}
        LOG.warn('send a update message, type: %s, uri: %s' % (mode, uri))
        LOG.debug('send a set command, message: %s', str(body))
        try:
            self._change_client.publisher_data_ext(exchange=CMDB_CONF.exchange_name, routing_key=topic, data=body)
        except Exception as e:
            LOG.error('Failed to publish set command: %s, %s' % (body, e))
            raise

        return True