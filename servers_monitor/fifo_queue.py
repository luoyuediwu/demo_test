#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""

import collections

class FifoQueue(object):
    """

    """
    def __init__(self,maxsize=1000):
        self.maxsize = maxsize
        self._queue = collections.deque()

    def append(self,item):
        self.append(item)

    def get_all(self):
        ret = list(self._queue)
        self._queue.clear()
        return ret

    def qsize(self):
        return len(self._queue)
