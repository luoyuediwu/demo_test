#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""

import os
import sys
import glob
import importlib

from flask import Flask
from flask_restful import Api
from oslo_log import log

from common.confs import prepare_service, write_pid_file
#from DataBase.test_common import ETL_RDB_CONF, FSS_CONF # 防止配置项注册失败，勿删


if __name__ != '__main__':
    import os
    __name__ = globals().get('__name__')
    __file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')


app = Flask(__name__)
api = Api(app)

LOG = log.getLogger(__name__)


def import_modules():
    """
    从 api_module 加载以 api_ 为前缀的子模块
    从环境变量 USED_API_MODULES 中读取需要实际的模块，用于测试。
    若环境变量存在，且值为空（''），则不会自动加载任何模块
    :return:
    """
    self_path = os.path.split(os.path.realpath(__file__))[0]
    api_modules = glob.glob(os.path.join(self_path, 'api_module/api_*.py*'))
    api_modules.extend(glob.glob(os.path.join(self_path, 'api_module/api_*.so')))
    avaiable_modules = set()

    used_modules = None
    if 'USED_API_MODULES' in os.environ:
        used_modules = set(os.environ['USED_API_MODULES'].split(','))

    for m in api_modules:
        basename = os.path.basename(m)
        module_name = os.path.splitext(basename)[0]
        if used_modules is None or (used_modules is not None and module_name[4:] in used_modules):
            avaiable_modules.add(module_name)

    avaiable_modules = sorted(list(avaiable_modules))
    for m in avaiable_modules:
        import_module(m)


def import_module(name):
    """
    导入单个模块
    :param name: 模块名称，模块必须位于 api_module 下
    """
    import_absulute_module('common.restful.api_module', name)


def import_absulute_module(module_path, name):
    """
    从任意路径装载一个API模块，用于测试或特殊用途
    可以加载 py、pyc 和 so 格式的扩展，同名的模块仅会加载一个，加载顺序为 so>py>pyc
    :param module_path: 要加载模块的路径
                         例如希望加载 common.restful.api_module.api_foo，则 module_path 值为 common.restful.api_module
    :param name:        要加载的模块名称
                         例如希望加载 common.restful.api_module.api_foo，则 name 值为 api_foo
    """
    full_module = '.'.join([module_path, name])
    module = importlib.import_module(full_module)
    module_init = getattr(module, 'api_module')
    if module_init is not None:
        try:
            module_init(api, app=app)
        except Exception as e:
            LOG.error("Error while loading '%s': %s" % (full_module, str(e)))
            sys.stderr.write("Error while loading '%s': %s\n" % (full_module, str(e)))
        LOG.info("Api module '%s' from registerd." % full_module)
    else:
        LOG.warn("Failed to load api module '%s'!" % full_module)


def hack_argv():
    """
    当使用 gunicorn 启动应用时，命令行参数会有冲突，所以此处采用环境变量传递参数，以保障参数解析能够通过
    :return: 构造或原生的命令行参数
    """
    if '--hardware' in sys.argv and '--product' in sys.argv:
        return sys.argv[1:]

    import os
    argv = ['--hardware', '', '--product', '']
    argv[1] = os.environ['HARDWARE']
    argv[3] = os.environ['PRODUCT']
    return argv


prepare_service('api', hack_argv())
import_modules()

if __name__ == '__main__':
    write_pid_file('rest_api')
    app.run("0.0.0.0", 5000)

