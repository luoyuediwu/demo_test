#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@brief 简介 
@details 详细信息
@author  luoyuediuw
@data    17-7-26
"""

import os
import sys

from oslo_config import cfg
from oslo_log import log

cfg.CONF.register_cli_opts([
    cfg.StrOpt('product', default='test', help=u'产品类型，决定配置文件'),
    cfg.StrOpt('hardware', default='', help=u'硬件类型，默认为服务器'),
    cfg.StrOpt('pid-file', short='p', default='/var/run/@APP@.pid', help=u'Write pid to file')
])

cfg.CONF.register_cli_opts([
    cfg.StrOpt('BASE_AGENT_SCRIPT_NAME', default='start_base_agent', help=u'启动基本进程的名称'),
    cfg.StrOpt('SUBSYSTEM_AGENT_SCRIPT_NAME', default='start_subsystem_agent', help=u'启动子系统的名称'),
    cfg.StrOpt('OTHERS_AGENT_SCRIPT_NAME', default='start_others_agent',help=u'启动其它进程的名称')
])

cfg.CONF.register_cli_opts([
    cfg.IntOpt(name='base_agent',
               default=1,
               help=u'监控cpu进程个数'),
    cfg.IntOpt(name='subsystem_agent',
               default=1,
               help=u'子系统监控进程的个数'),
    cfg.IntOpt(name='other_agent',
               default=1,
               help=u'redis、数据库'),
])

cfg.CONF.register_cli_opts([
    cfg.IntOpt(name='base_agent',
               default=1,
               help=u'监控cpu进程个数'),
    cfg.IntOpt(name='subsystem_agent',
               default=1,
               help=u'子系统监控进程的个数'),
    cfg.IntOpt(name='other_agent',
               default=1,
               help=u'redis、数据库'),
])

cfg.CONF.register_cli_opts([

    cfg.StrOpt('fss_inner_exchange',
               default='fss_exchange',
               help=u'对外exchange，包括实时数据、事件发布，设置点、调试、数据获取、测试板卡、测试连接'),
    cfg.StrOpt('fss_realvalue_topic',
               default='fss.value',
               help=u'实时数据topic'),
    cfg.StrOpt('fss_realvalue_target',
               default='process_value',
               help=u'实时数据target'),
    cfg.IntOpt('real_value_ttl',
               default=600000,
               help=u'实时数据队列的ttl'),
])

COMMON_CONF = cfg.CONF


def prepare_service(log_name=None, argv=None):
    """
    初始化服务，所有服务进程应调用此接口而不要自行实现
    :param log_name: 日志配置文件名称
    :param argv: 命令行参数，若未提供则使用 sys.argv 作为命令行
    """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    # 初始化基本的配置、日志等环境信息
    if argv is None:
        argv = sys.argv[1:]
    log.register_options(cfg.CONF)
    cfg.CONF(argv)
    cfg.CONF(argv, project=COMMON_CONF.product)
    if log_name is not None:
        cfg.CONF.log_config_append = "/opt/%s/etc/%s/logger_%s.conf" % (COMMON_CONF.product, COMMON_CONF.product, log_name)
    log.setup(cfg.CONF, COMMON_CONF.product)


def write_pid_file(app_name):
    """
    将当前进程的 PID 写入文件
    :param app_name: 进程名称或路径
    """
    pid = COMMON_CONF.pid_file
    if not pid:
        pid = '/var/run/@APP@.pid'
    app_name = app_name.replace('\\', '/')
    if '/' in app_name:
        app_name = app_name.split('/')[-1]
    if '.' in app_name:
        app_name = app_name[0:app_name.rfind('.')]
    pid = pid.replace('@APP@', app_name)
    print('Write pid %d to file %s' % (os.getpid(), pid))

    with open(pid, 'w') as f:
        f.write('%d\n' % os.getpid())
