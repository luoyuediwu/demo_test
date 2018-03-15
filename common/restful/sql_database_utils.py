#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief    : 简介 
@details  : 详细信息
@author   : luoyuediwu
@data     : 2017-04-24 18:31
@Filename : sql_database_utils
"""
import os
import sys

from common.constant_define import DictParam, QueryOperation


def _format_v(v):
    """
    modified by wangzhan @ 2016-06-21
    生成 SQL 参数时，对于 MySql xx > '12' 这样的表达式，当字段 xx 类型为数字时，可自动转义
    对于 sqlite，若 xx 类型为 int，必须使用 xx > 12，不能加引号，否则查不出来
    为保持多种数据库兼容，这里根据输入参数进行转义。若输入参数类型是数字就不加引号，否则加上引号。
    :param v: 原始数据
    :return: 转换后的数据
              若原始数据为数字，则直接转成字符串
              若原始数据为字符串，则转义成 '字符串' 格式
              若原始数据为列表，将对列表中每个元素单独转义
    """
    if isinstance(v, (int, float)):
        return str(v)
    elif isinstance(v, (str, unicode)):
        return u"'%s'" % SqlDatabaseUtilsMinxin.addslashes(v)
    elif isinstance(v, list):
        return [_format_v(e) for e in v]
    else:
        return u"'%s'" % str(v)


class SqlDatabaseUtilsMinxin:

    OP = QueryOperation

    op_trans = {
        OP.in_: lambda v: u"in (" + u", ".join(_format_v(v)) + u")" if isinstance(v, list) else u"in (%s)" % _format_v(v),
        OP.notin: lambda v: u"not in (" + u", ".join(_format_v(v)) + u")" if isinstance(v, list) else u"not in (%s)" % _format_v(v),
        OP.lt: lambda v: u"< {}".format(_format_v(v)),
        OP.gt: lambda v: u"> {}".format(_format_v(v)),
        OP.lte: lambda v: u"<= {}".format(_format_v(v)),
        OP.gte: lambda v: u">= {}".format(_format_v(v)),
        OP.neq: lambda v: u"!= {}".format(_format_v(v)),
        OP.eq: lambda v: u"= {}".format(_format_v(v)),
    }

    op_trans_mysql = {
        OP.like: lambda v: u"like '{}' ESCAPE '\\\\'".format(v.replace('_', r'\_').replace('?', '_')),
    }
    op_trans_mysql.update(op_trans)

    op_trans_sqlite = {
        OP.like: lambda v: u"like '{}' ESCAPE '\\'".format(v.replace('_', r'\_').replace('?', '_')),
    }
    op_trans_sqlite.update(op_trans)

    def build_op(self, op, val):
        """
        根据操作符和操作数生成正确的 SQL where 语句
        :param op:  操作符字符串
        :param val: 要操作的值，请确保格式正确
        :return: 组装好的查询语句
        """
        raise NotImplementedError()

    # 生成查询条件中 page 部分对应的SQL语句
    @staticmethod
    def build_query_limit(params):
        if DictParam.page not in params or not params[DictParam.page]:
            return ' '
        offset = 0 if params[DictParam.page][DictParam.number] <= 1 else \
            (int(params[DictParam.page][DictParam.number]) - 1) * int(params[DictParam.page][DictParam.size])
        return " LIMIT {0} OFFSET {1}".format(params[DictParam.page][DictParam.size], offset)

    # 生成查询条件中 where 字段对应的SQL语句
    def build_query_where(self, params, prefix="WHERE"):
        if DictParam.where not in params or not params[DictParam.where]:
            return ' '
        where = []
        for _or in params[DictParam.where]:
            ands = []
            for _and in _or[DictParam.terms]:
                ands.append(" `{0}` {1} "
                            .format(_and[DictParam.field],
                                    self.build_op(_and[DictParam.operator], _and[DictParam.value])))
            if ands:
                where.append(' (' + ' AND '.join(ands) + ') ')
        return " %s (" % prefix + ' OR '.join(where) + ')' if where else ''

    # 生成查询条件中 orders 对应的SQL语句
    @staticmethod
    def build_query_order_by(params):
        if DictParam.sorts not in params or not params[DictParam.sorts]:
            return ' '
        orders = []
        for s in params[DictParam.sorts]:
            orders.append(" `{0}` {1} ".format(s[DictParam.field], s[DictParam.type_]))
        return " ORDER BY " + ', '.join(orders) if orders else ''

    @staticmethod
    def addslashes(text):
        """
        为字符串添加适用于数据库的斜杠
        :param text: 字符串
        :type text: str
        :return: 添加斜杠后的字符串
        """
        return text.replace(u'\\', u'\\\\')\
            .replace(u"'", u"\\'")\
            .replace(u"\n", u"\\n")\
            .replace(u'"', u'\\"')


class MySqlDatabaseUtilsMinxin(SqlDatabaseUtilsMinxin):
    def build_op(self, op, val):
        return self.op_trans_mysql[op](val)


class SqliteDatabaseUtilsMinxin(SqlDatabaseUtilsMinxin):
    def build_op(self, op, val):
        return self.op_trans_sqlite[op](val)