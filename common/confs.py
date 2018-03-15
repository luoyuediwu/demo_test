#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/25 20:26
# @Author  : luoyuediwu
# @Site    : 
# @File    : confs.py
# @Software: PyCharm

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/4/25 20:23
# @Author  : luoyuediwu
# @Site    :
# @File    : confs.py
# @Software: PyCharm
import os
import sys
from oslo_config import cfg
from oslo_log import log
cfg.CONF.register_cli_opts([cfg.StrOpt('product', default='test', help=u'\u4ea7\u54c1\u7c7b\u578b\uff0c\u51b3\u5b9a\u914d\u7f6e\u6587\u4ef6'),
                            cfg.StrOpt('hardware', default='', help=u'\u786c\u4ef6\u7c7b\u578b\uff0c\u9ed8\u8ba4\u4e3a\u670d\u52a1\u5668'),
                            cfg.StrOpt('pid-file', short='p', default='/var/run/@APP@.pid', help=u'Write pid to file')]
                        )
COMMON_CONF = cfg.CONF

def prepare_service(log_name = None, argv = None):
    """
    初始化服务，所有服务进程应调用此接口而不要自行实现
    :param log_name: 日志配置文件名称
    :param argv: 命令行参数，若未提供则使用 sys.argv 作为命令行
    """
    reload(sys)
    sys.setdefaultencoding('utf-8')
    if argv is None:
        argv = sys.argv[1:]
    log.register_options(cfg.CONF)
    cfg.CONF(argv)
    cfg.CONF(argv, project=COMMON_CONF.product)
    if log_name is not None:
        cfg.CONF.log_config_append = '/opt/demo_%s/etc/%s/logger_%s.conf' % (COMMON_CONF.product, COMMON_CONF.product, log_name)
    log.setup(cfg.CONF, COMMON_CONF.product)
    return


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
    print 'Write pid %d to file %s' % (os.getpid(), pid)
    with open(pid, 'w') as f:
        f.write('%d\n' % os.getpid())
