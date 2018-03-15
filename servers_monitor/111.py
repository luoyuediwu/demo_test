#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/4 15:49
# @Author  : luoyuediwu
# @Site    : 
# @File    : 111.py
# @Software: PyCharm
import time
import json
from db.redis_operate import *
Rp = RedisOperate()
def get_snapvalue():
    ret = []
    ids = {"resources": [{"resources_id": "ip_0"},{"resources_id": "ip_1"}]}
    try:
        if isinstance(ids, dict):
            _ids = ids.values()[0]
        else:
            _ids = ids
        t = int(time.time())
        for item in _ids:
            if not item.values()[0]:
                continue
            ret.append(item["resources_id"])
        print ret
        key_value = Rp.get_values(ret)
    except Exception as ee:
        print "fsdfsdfs"
if __name__ == "__main__":
    get_snapvalue()