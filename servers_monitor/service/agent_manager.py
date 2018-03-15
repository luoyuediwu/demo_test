#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@brief 简介 
@details 详细信息
@author  wanghe
@data    15-7-4 
'''

import collections
import subprocess
import os
from eventlet import semaphore
from oslo_log import log

import os
__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)


class AgentManager(object):

    def __init__(self, name):
        self._group_device = collections.defaultdict(set)  # 存储组到设备的映射
        self._proc = None  # 进程信息
        self._name = name  # agent名称
        #self._agent_script = get_agent_script(agent_script_name)
        self._agent_script = '/opt/demo_test/servers_monitor/parmiko_utils.py'
        self._update_queue = collections.deque()  # ip_server更新队列
        self._update_mutex = semaphore.Semaphore()  # ip_server更新锁
        self._running = False

    def start(self):
        """
        启动采集器
        @return:
        """
        args = ['python', self._agent_script, "--agent_name", self._name, "--product", 'test',
                "--hardware", 'general']
        self._proc = subprocess.Popen(args)
        LOG.warn('%s start, pid: %d', self._name, self._proc.pid)

    def stop(self):
        """
        停止采集器
        @return:
        """
        if self._proc is not None:
            try:
                self._proc.kill()
            except Exception as ee:
                LOG.warn('%s kill error', self._name)
            self._running = False
            LOG.warn('%s is already stopped', self._name)

    def check(self):
        """
        检查采集器是否存在
        @return:
        """
        if self._proc is None:
            return False
        try:
            os.kill(self._proc.pid, 0)
        except OSError:
            return False
        return True

    def delete(self, group, device_id):
        """
        删除采集器中的服务器
        @param group: 设备所属组
        @param device_id:
        @return:
        """
        with self._update_mutex:
            self._group_device[group].remove(device_id)

    def add(self, group, device_id):
        """
        向采集器中添加服务器
        @param group: 设备所属组
        @param device_id:
        @return:
        """
        with self._update_mutex:
            self._group_device[group].add(device_id)
