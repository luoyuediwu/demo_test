#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 9:35
# @Author  : luoyuediwu
# @Site    : 
# @File    : page_info.py
# @Software: PyCharm



import os
import json
from flask_restful import Resource
from common.restful.restful_utils import RestfulUtilsMixin
from common.confs import COMMON_CONF
from DataBase.db.rdb.test_database_connection import TESTDatabaseConnection2
from app.lib.storage.cache import AuthCacheBackendFactory
from app.lib.request_utils import *
from logagent.log_api import write_oplog
from common.constant_define import Commconstant
PIC_FILE_PREIFX = '/opt/xbrother_{0}/upload/'.format(COMMON_CONF.product)
__version__ = '1.0.0.0'

class PageInfo(Resource, RestfulUtilsMixin,Commconstant):

    def get_session(self):
        request_ip = request_remote_ip()
        session = request_session()
        cache = AuthCacheBackendFactory.new()
        account = cache.user_for_session(session)
        return (request_ip, account)

    def get(self):
        """
                获取页面配置信息，具体参见设计文档章节“3.3.19.1”
        {
            "login_title": "数据中心运维管理系统",
            "host_title": "让数据中心更简单",
            "copyright": "深圳市共济科技股份有限公司",
            "login_logo": "logo.png",
            "host_logo”: “logo.png”,
            "flush_period": "3",
            "enable_3d": "1"
        }
        字段编码    含义及取值范围
        login_title     登录页标题
        host_title      首页标题
        copyright       版权信息
        login_logo      登录页面logo
        host_logo       页面导航栏logo
        flush_period    工程组态刷新频率
        enable_3d       启用3D：
                    0：不启用
                    1：启用
        :return:
        """
        return self.rest_execute_action('get')

    def post(self):
        """
         设置页面配置信息，具体参见设计文档章节“3.3.19.2”
        上传参数
        {
            "login_title": "数据中心运维管理系统",
            "host_title": "让数据中心更简单",
            "login_logo": "logo.png",
            "host_logo”: “logo.png”,
            "copyright": "深圳市共济科技股份有限公司",
            "flush_period": "3",
            "enable_3d": "1"
        }
        :return:
        """
        return self.rest_execute_action('post')

    def _get_naked(self):
        return self.rest_success(data=self._get_page_info())

    def _post_naked(self):
        request_ip, account = self.get_session()
        args = self.rest_load_request()
        data_field = ['login_title',
         'host_title',
         'login_logo',
         'host_logo',
         'copyright',
         'flush_period',
         'enable_3d']
        for field in args:
            if field not in data_field:
                return self.rest_result(self.R.EC.INVALID_PARAM, extra_text='{0}'.format(field))
            if field == 'enable_3d' and int(args[field]) != 0 and int(args[field]) != 1:
                return self.rest_result(self.R.EC.INVALID_PARAM_FORMAT, extra_text='{0} value must 0 or 1'.format(field))
            if field == 'login_logo' or field == 'host_logo':
                if not os.path.exists(PIC_FILE_PREIFX + args[field]):
                    return self.rest_result(self.R.EC.INVALID_PARAM, extra_text='{0} file not exits'.format(args[field]))

        page_conf_data = self._get_page_info()
        if page_conf_data:
            if page_conf_data.get('login_logo') and args.get('login_logo') and page_conf_data.get('login_logo') != args['login_logo'] and os.path.exists(PIC_FILE_PREIFX + page_conf_data.get('login_logo')):
                os.remove(PIC_FILE_PREIFX + page_conf_data.get('login_logo'))
            if page_conf_data.get('host_logo') and args.get('host_logo') and page_conf_data.get('host_logo') != args['host_logo'] and os.path.exists(PIC_FILE_PREIFX + page_conf_data.get('host_logo')):
                os.remove(PIC_FILE_PREIFX + page_conf_data.get('host_logo'))
        else:
            page_conf_data = {}
        page_conf_data.update(args)
        conn_gudb = TESTDatabaseConnection2()
        sql_str = "update project_setting set content='{0}' where set_type='page_info' ".format(json.dumps(page_conf_data, ensure_ascii=False))
        conn_gudb.raw_execute(sql_str)
        write_oplog.writelog(user=account, module='\xe9\xa1\xb5\xe9\x9d\xa2\xe9\x85\x8d\xe7\xbd\xae', type=3, ip=request_ip, desc='\xe6\x9b\xb4\xe6\x94\xb9\xe7\xb3\xbb\xe7\xbb\x9f\xe9\xa1\xb5\xe9\x9d\xa2\xe5\x8f\x82\xe6\x95\xb0', result=0, args=str(args))
        return self.rest_success()

    def _get_page_info(self):
        conn_db = TESTDatabaseConnection2()
        sql_str = 'select content from project_setting where set_type="page_info"'
        query_data = conn_db.raw_query(sql_str)
        if len(query_data) <= 0:
            return {}
        for data in query_data:
            return json.loads(data['content'])


