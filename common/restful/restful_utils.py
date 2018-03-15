#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 11:36
@Filename : restful_utils
"""
import os
import sys
import traceback
from flask import request,Flask
from flask_restful import Api
from werkzeug import exceptions
from restful_define import *
import json
app = Flask('__main__')
api = Api(app)

registry = []

def get_registry():
    return registry

def get_app():
    return app

def get_api():
    return api

class RestfulUtilsMixin:

    class R:
        RC = RestfulResponseCode
        EC = RestfulErrorCode

    class Param:
        def __init__(self, key, type_, required=False, help_=False, location=None):
            self.key = key
            self.type = type_
            self.required = required
            self.help = help_
            self.location = location

    bad_request_errors = (
        R.EC.PARAM_TOO_LONG[0],
        R.EC.PARAM_LOST[0],
        R.EC.INVALID_PARAM_FORMAT[0],
        R.EC.INVALID_JSON_FORMAT[0],
        R.EC.REQUEST_TOO_LARGE[0],
        R.EC.UNKNOWN_INTERFACE[0],
        R.EC.PARAM_EMPTY[0],
        R.EC.REPEATED_PARAM[0],
        R.EC.EMPTY_POST_DATA[0],
        R.EC.DATE_FORMAT_ERROR[0],
        R.EC.DATE_RANGE_ERROR[0],
    )

    unauthorized_error = (
        R.EC.UNAUTHORIZED[0],
    )

    forbidden_errors = (
        R.EC.NEED_LOGIN[0],
        R.EC.NO_PERMISSION[0],
    )

    not_found_errors = (
        R.EC.ITEM_NOT_FOUND[0],
    )

    def rest_execute_action(self, act):
        """
        执行实际的动作方法，实际的方法名为 _<act>_naked
        :param self: 当前 RESTful处理对象
        :param act: 动作名称
        :return: RESTful 状态信息与错误码
        """
        try:
            return getattr(self, '_' + act + '_naked')()
        except RestfulError as e:
            return self.rest_result(e.error_code)
        except exceptions.BadRequest as e:
            full_message = "\n".join(key + ":" + e.data['message'][key] for key in e.data['message'])
            return self.rest_result(self.R.EC.PARAM_EMPTY, response_code=e.code, extra_text=full_message)
        except Exception as e:
            return self.rest_result(self.R.EC.UNKNOWN_ERROR, extra_text='Exception is '+str(e))

    @staticmethod
    def rest_load_request():
        """
        将请求按照 Json 格式进行解析，并转换为对象
        :return: 转换后的对象，若转换失败则抛出异常
        """
        try:
            return json.loads(request.data)
        except ValueError as e:
            raise RestfulError(RestfulErrorCode.INVALID_JSON_FORMAT, e.message)

    @staticmethod
    def load_request_params(template):
        """
        从 GET 请求的参数中获取并校验对应的值
        :param template: 字典，表示按照何种方式从请求参数中取值，内容格式为：
        {
            '<参数键名称>': {'type': <数据类型>, 'required': False, 'help': '错误文本'}
        }
        其中数据类型可选 int, float, str 和 list。 list 表示字符串的列表，以半角逗号(,)或分号(;)隔开
        除 type 字段外，其他字段均可省略
        :return: 字典格式，其中键为 temlpate 中的各个键，值为解析后的值。若对应的值缺失则为 None
        """
        from flask_restful import reqparse

        def str_list(value):
            import re
            return re.split('[,;]', value)

        parser = reqparse.RequestParser()
        for titem in template:
            ''':type titem: self.Param'''
            if titem.location:
                parser.add_argument(titem.key,
                                    type=titem.type if titem.type != list else str_list,
                                    required=titem.required,
                                    help=titem.help,
                                    location=titem.location)
            else:
                parser.add_argument(titem.key,
                                    type=titem.type if titem.type != list else str_list,
                                    required=titem.required,
                                    help=titem.help)
        return parser.parse_args()

    def rest_success(self, data=None):
        """
        返回一个成功请求，可附带数据
        :param data: 可选的数据
        :return: Flask 请求反馈对象，包含成功数据
        """
        return self.rest_result(self.R.EC.SUCCEED, self.R.RC.OK, data)

    def rest_failed(self, error_code, extra_text=None):
        """
        返回一个失败状态
        :param error_code: 失败原因的错误码，HTTP状态码会根据错误码自动指定
        :param extra_text: (optional) 额外的错误文本
        :return: Flask 请求反馈对象，包含失败数据和错误码
        """
        return self.rest_result(error_code=error_code, extra_text=extra_text)

    def rest_result(self, error_code, response_code=-1, data=None, extra_text=None):
        """
        返回指定的 Restful 状态，可包含附加数据
        :param error_code: 来自 RestfulResponseCode 的错误码
        :param response_code: HTTP 返回码, 若取值为 -1 则根据 error_code 自行决定
        :param data: 可选的数据
        :param extra_text: 可选的附加错误信息
        :return: Flask 请求反馈对象
        """
        if response_code == -1:
            if error_code[0] == self.R.EC.SUCCEED[0]:
                response_code = self.R.RC.OK
            elif error_code[0] in self.bad_request_errors:
                response_code = self.R.RC.BAD_REQUEST
            elif error_code[0] in self.not_found_errors:
                response_code = self.R.RC.NOT_FOUND
            elif error_code[0] in self.unauthorized_error:
                response_code = self.R.RC.UNAUTHORIZED
            elif error_code[0] in self.forbidden_errors:
                response_code = self.R.RC.FORBIDDEN
            else:
                response_code = self.R.RC.SERVER_ERROR
        result = self.R.EC.format_error_code(self.R.EC.code_with_info(error_code, extra_text) if extra_text else error_code)
        if data:
            result['data'] = data

        return result, response_code
