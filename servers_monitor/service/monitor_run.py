#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import sys
import time
from oslo_config import cfg
from oslo_service import service as os_service
from oslo_log import log
from servers_monitor.parmiko_utils import *
COMMON_CONF = cfg.CONF

LOG = log.getLogger(__name__)

class ServerMontior(os_service.Service):

    def __init__(self,threads=2):
        super(ServerMontior,self).__init__(threads=threads)

    def start(self):
        super(ServerMontior,self).start()
        self.create_worker()
    def test2(self):
        putil = ParmikoUtils('tools.conf')
        putil.get_trans()
        # putil.do_cmds(['ls -ll','monit summary'])
        putil.get_file_resources()
        # putil.down_files(r'C:\11',r'/root/test/')
        print putil.server_info

    def create_worker(self):
        self.tg.add_thread(self.test2)

def prepare_sevice(argv=None):
    log.register_options(cfg.CONF)
    if argv is None:
        argv = sys.argv
    cfg.CONF.log_config_append = "E:/test_ui/servers_monitor/logger_agent_manager.conf"
    cfg.CONF(argv[1:],project='test')

if __name__ == '__main__':
    prepare_sevice()
    service = ServerMontior()
    launcher = os_service.launch(cfg.CONF,service)
    launcher.wait()
