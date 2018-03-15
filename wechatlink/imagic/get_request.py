#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/5 15:53
# @Author  : luoyuediwu
# @Site    : 
# @File    : get_request.py
# @Software: PyCharm

import requests
import json

def get_token():
    payload_access_token={
        'grant_type':'client_credential',
        'appid':'wx71e1a38f5d00d4d4',
        'secret':'2e1cf9d8f982ea2e58d47138a4fed0e8'
    }
    token_url='https://api.weixin.qq.com/cgi-bin/token'
    r=requests.get(token_url,params=payload_access_token)
    dict_result= (r.json())
    print dict_result['access_token']
    return dict_result['access_token']

yourtoken = get_token()
url="https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=%s"%yourtoken

datas={
    "type":"image",
    "offset":0,
    "count":20
}
data = json.dumps(datas)
a=requests.post(url=url,data =data)
print(a.text)