#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
from oslo_config import cfg
from constant_define import *
CMDB_GROUP = 'CMDB'
cfg_opts = [cfg.StrOpt('mongodb_ip', default=MongoParam.mongo_ip),
 cfg.IntOpt('mongodb_port', default=MongoParam.mongo_port),
 cfg.StrOpt('mongodb-guest', default=MongoParam.mongodb_guest),
 cfg.StrOpt('mongodb-pwd', default=MongoParam.mongodb_pwd),
 cfg.StrOpt('mongodb_db', default=MongoParam.mongodb_db),
 cfg.StrOpt('backend', default=MongoParam.mongodb_db),
 cfg.BoolOpt('slaveok', default=MongoParam.slaveok)]

cfg.CONF.register_opts(cfg_opts, group=CMDB_GROUP)

CMDB_CONF = cfg.CONF.CMDB
