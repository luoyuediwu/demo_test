#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/12 18:44
# @Author  : luoyuediwu
# @Site    : 
# @File    : pymono_test.py
# @Software: PyCharm

import pymongo
import pymongo.collection

connection = pymongo.MongoClient("127.0.0.1",27017)
mongo_conn_db = connection["dcs_cmdb"]
print "asdasdad"
mongo_conn_db.versions.insert({ "_id" : "case2", "version" : 300 })
print "结束"
