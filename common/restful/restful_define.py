#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 12:46
@Filename : restful_define
"""
import os
import sys

class RestfulResponseCode:
    """
    RESTful 接口的 HTTP 返回码常量定义
    位于概要设计章节 2.5.2.4 接口响应码及错误响应主体定义
    """
    OK = 200
    NO_CONENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    SERVER_ERROR = 500


class RestfulErrorCode:
    """
    RESTful 请求错误的错误码与默认错误文本
    位于概要设计章节 2.5.2.4 接口响应码及错误响应主体定义
    """
    SUCCEED = ('00', 'Succeed')
    UNAUTHORIZED = ('01', 'Username or password error')
    RESOURCE_NOT_FOUND = ('02', 'Resource not found')
    REQUEST_TIME_OUT = ('03', 'Request timeout')
    PARAM_TOO_LONG = ('04', 'Params too long')
    PARAM_LOST = ('05', 'Param lost')
    INVALID_PARAM_FORMAT = ('06', 'Invalid param format')
    RESOURCE_IS_EMPTY = ('07', 'Resource is empty')
    INVALID_JSON_FORMAT = ('08', 'Invalid json format')
    REQUEST_TOO_LARGE = ('09', 'Request too large')
    SYSTEM_BUSY = ('10', 'System busy, please try agein later')
    UNKNOWN_INTERFACE = ('11', 'Unknown interface')
    PARAM_EMPTY = ('12', 'Params is empty')
    REPEATED_PARAM = ('13', 'Repeated param')
    EMPTY_POST_DATA = ('14', 'Post data is empty')
    DATE_FORMAT_ERROR = ('15', 'Date format error')
    DATE_RANGE_ERROR = ('16', 'Date range error')

    NEED_LOGIN = ('41', 'This operation need login')
    NO_PERMISSION = ('43', 'No permission for this resource')

    ITEM_NOT_FOUND = ('44', 'Item not found')
    DATABASE_ERROR = ('51', 'Database operation failed')
    ACQUISITION_ERROR = ('52', 'Acquisiton module response an error code')
    INVALID_PARAM = ('53', 'Invalid parameter')
    FILESYSTEM_ERROR = ('61', 'Failed to operate file system')

    UNKNOWN_ERROR = ('99', 'Unknown Error')

    @staticmethod
    def code_with_info(code, text):
        """
        将错误码附加上自定义文本
        :param code: 错误码，必须是此类中定义的变量之一
        :param text: 额外的错误文本
        :return: 错误码和附加后的文本
        """
        return code[0], code[1] + ': ' + text

    @staticmethod
    def format_error_code(code):
        """
        将错误码格式化成 Restful 需要的返回内容格式
        :param code:
        :return:
        """
        return {
            'error_code': code[0],
            'error_msg': code[1]
        }


class RestfulError(Exception):
    """
    RESTful 异常，以 RestfulErrorCode 类中定义的错误码值作为初始化参数
    """
    def __init__(self, error_code, ext_msg=None, response_code=RestfulResponseCode.SERVER_ERROR):
        self.error_code = error_code
        self.response_code = response_code
        if ext_msg:
            self.error_code = RestfulErrorCode.code_with_info(error_code, ext_msg)
        super(RestfulError, self).__init__(RestfulErrorCode.format_error_code(self.error_code))

    def format_message(self):
        return RestfulErrorCode.format_error_code(self.error_code)