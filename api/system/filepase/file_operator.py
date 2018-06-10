#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/14 10:40
# @Author  : luoyuediwu
# @Site    : 
# @File    : file_operator.py
# @Software: PyCharm
import os
from common.restful.restful_utils import RestfulUtilsMixin
from oslo_log import log
from common.confs import COMMON_CONF
from tools.parse_execl import OperateExecle
import eventlet
from eventlet import Event

__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)
__version__ = '1.0.0.0'
EXPORT_ROOT = '/opt/%s/download/eventrules' % COMMON_CONF.product
class FilePaseToJson(RestfulUtilsMixin):
    def __init__(self):
        pass
    def make_pase(args):
        evt = args['evt']
        full_path = args['full_path']
        try:
            Operecle = OperateExecle(full_path)
            data = Operecle.execltojson(u'测试用例集')
            evt.send(data)
        except Exception as e:
            LOG.error('make_import:{0}'.format(e))
            evt.send(''.format(e))

