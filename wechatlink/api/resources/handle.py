#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""

# -*- coding: utf-8 -*-
# filename: handle.py
# -*- coding: utf-8 -*-
# filename: handle.py
import os
import sys
from flask_restful import Resource, reqparse
from flask import make_response
from common.restful.restful_utils import *
import hashlib
import lxml
from lxml import etree
import os
import time
from wechatlink.rebort import TulingAutoReply

key = "5790ddc3a53544dbb930826a5a55d389"
url = "http://www.tuling123.com/openapi/api"

auto_repaly = TulingAutoReply(key,url)

class Handle(Resource,RestfulUtilsMixin):

    def get(self):
        return self.rest_execute_action('get')

    def post(self):
        return self.rest_execute_action('post')

    def _get_naked(self):
        data = self.rest_load_request()
        try:
            if len(data) == 0:
                return "hello, this is handle view"
            signature = data.signature
            timestamp = data.timestamp
            nonce = data.nonce
            echostr = data.echostr
            token = "luoyuediwu"  # 请按照公众平台官网\基本配置中信息填写

            list = [token, timestamp, nonce]
            list.sort()
            sha1 = hashlib.sha1()
            map(sha1.update, list)
            hashcode = sha1.hexdigest()
            print "handle/GET func: hashcode, signature: ", hashcode, signature
            if hashcode == signature:
                return self.rest_success(echostr)
            else:
                return self.rest_success()
        except Exception, Argument:
            return self.rest_failed()
        return self.rest_success()

    def _post_naked(self):
        str_xml = self.rest_load_request()
        xml = etree.fromstring(str_xml)
        content =xml.find("Content").text
        msgType = xml.find("MsgType").text
        fromUser = xml.find("FromUserName").text
        toUser = xml.find("ToUserName").text
        print content
        if msgType == "text":
            replay = auto_repaly.reply(content).replace("n",'')+"\n"+u"     -----来着秀秀女神机器人"
            if replay is not None:
                pass
            else:
                replay = u"不知道你说了啥~"
            xml_rep = "<xml><ToUserName><![CDATA[%s]]></ToUserName><FromUserName><![CDATA[%s]]></FromUserName><CreateTime>%s</CreateTime><MsgType><![CDATA[text]]></MsgType><Content><![CDATA[%s]]></Content><FuncFlag>0</FuncFlag></xml>"
            response = make_response(xml_rep % (fromUser,toUser,str(int(time.time())), content))
            response.content_type = 'application/xml'
            return response
        if msgType == "image":
            return "hahhhhaa"

        if msgType == "voice":
            print "语音"

