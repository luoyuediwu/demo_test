#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/12/5 14:29
# @Author  : luoyuediwu
# @Site    : 
# @File    : get_image.py
# @Software: PyCharm
import requests

def get_media_ID(path):
    img_url='https://api.weixin.qq.com/cgi-bin/material/add_material'
    payload_img={
        'access_token':get_token(),
        'type':'image'
    }
    data ={'media':open(path,'rb')}
    r=requests.post(url=img_url,params=payload_img,files=data)
    dict =r.json()
    print dict
    print dict['media_id']
    return dict['media_id']

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

get_token()
get_media_ID(path="/opt/imagic/11.PNG")
