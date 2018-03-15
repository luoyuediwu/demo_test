#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/28 13:39
# @Author  : luoyuediwu
# @Site    : 
# @File    : single_meta.py
# @Software: PyCharm

class SingleMeta(type):
    """单例"""
    def __init__(cls, what, bases=None, dict=None):
        super(SingleMeta, cls).__init__(what, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SingleMeta, cls).__call__(*args, **kwargs)
        return cls._instance

