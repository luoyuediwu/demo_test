#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import collections
import subprocess
import os
from eventlet import semaphore
from oslo_log import log

import os
__name__ = globals().get('__name__')
__file__ = os.path.join('/opt/log/', __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)

class ServiceManager(object):

    def __init__(self):
        self._manager_script = '/opt/demo_test/servers_monitor/parmiko_utils.py'
        self._name = 'parmiko_utils'
    def start(self):
        """
        启动进程
        :return:
        """
        args = ['python', self._manager_script]
        self._proc = subprocess.Popen(args)
        LOG.warn('%s start, pid: %d', self._name, self._proc.pid)

    def stop(self):
        if self._proc is not None:
            try:
                self._proc.kill()
            except Exception as ee:
                LOG.warn('%s kill error', self._name)
            self._running = False
            LOG.warn('%s is already stopped', self._name)

    def check(self):
        """
        check porc
        :return:
        """
        if self._proc is None:
            return False
        try:
            os.kill(self._proc.pid, 0)
        except OSError:
            return False
        return True




