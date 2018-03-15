#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import eventlet
eventlet.monkey_patch()

import sys

from oslo_config import cfg

from oslo_service import service as os_service
from confs import write_pid_file
from servers_monitor.service.agent_manager import *
import time

LOG = log.getLogger(__name__)


def prepare_service():
    """
    读取cfg，设置日志
    @return:
    """
    log.register_options(cfg.CONF)
    cfg.CONF(sys.argv[1:])
    cfg.CONF(sys.argv[1:], project='test')
    cfg.CONF.log_config_append = "/opt/demo_test/etc/test/logger_servers_manager.conf"
    log.setup(cfg.CONF, 'test')

class ServerMontior(os_service.Service):

    def __init__(self,threads=2):
        super(ServerMontior,self).__init__(threads=threads)

    def start(self):
        super(ServerMontior,self).start()
        self.create_worker()
    def test2(self):
        server_monitor = AgentManager('agent')
        while True:
            server_monitor.start()
            time.sleep(1000)


    def create_worker(self):
        self.tg.add_thread(self.test2)

def start():
    """
    启动入口
    :return:
    """
    prepare_service()
    service = ServerMontior()
    write_pid_file('perform_manager')
    launcher = os_service.launch(cfg.CONF,service)
    launcher.wait()

if __name__ == '__main__':
    sys.exit(start())
