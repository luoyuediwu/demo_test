#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 通过对pid文件的文件锁定检查，识别是否已有存在的实例
@author  wuhuafeng
@data    2016-01-13 
"""

import os
import tempfile

from oslo_log import log

import os
__name__ = globals().get('__name__')
__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)


class SingleInstance(object):
    """
    SingleInstance
    通过对pid文件的文件锁定检查，识别是否已有存在的实例
    """

    def __init__(self, pid_filename):
        self.fd = None
        self.fp = None
        self.initialized = False
        self.lockfile = os.path.normpath('{0}/{1}.lock'.format(tempfile.gettempdir(), pid_filename))
        self.pidfile = os.path.normpath('{0}/{1}.pid'.format(tempfile.gettempdir(), pid_filename))

    def lock_instance(self):
        """
        锁定进程pid文件实例，成功说明还未有其他实例，失败则说明已有存在的实例
        @return: True表示锁定成功，尚未有其他实例；False表示锁定失败，已有其他实例
        """
        import sys
        self.initialized = False
        if sys.platform == 'win32':
            try:
                # file already exists, we try to remove (in case previous
                # execution was interrupted)
                if os.path.exists(self.lockfile):
                    os.unlink(self.lockfile)
                self.fd = os.open(
                    self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            except OSError:
                LOG.warn('An process instance with {0} exist'.format(self.lockfile))
                return False
        else:  # non Windows
            import fcntl
            self.fp = open(self.lockfile, 'w')
            try:
                fcntl.lockf(self.fp, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except IOError:
                LOG.warn('An process instance with {0} exist'.format(self.lockfile))
                return False
        self.initialized = True
        return True

    def write_pid_to_file(self):
        """
        写入进程pid到pid文件
        """
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
        open(self.pidfile, 'w').write(str(os.getpid()))

    def read_pid_from_file(self):
        """
        获取文件中写入的pid
        @return: pid
        """
        if os.path.exists(self.pidfile):
            pid = int(open(self.pidfile).read())
            return pid
        return None

    def free_instance(self):
        """
        释放
        @return:
        """
        import sys
        import os
        if not self.initialized:
            return
        try:
            if sys.platform == 'win32':
                if hasattr(self, 'fd'):
                    os.close(self.fd)
                    os.unlink(self.lockfile)
            else:
                import fcntl
                fcntl.lockf(self.fp, fcntl.LOCK_UN)
                # os.close(self.fp)
                if os.path.isfile(self.lockfile):
                    os.unlink(self.lockfile)
        except Exception as e:
            LOG.error('Free single instance raise exception')
            LOG.exception(e)
        finally:
            self.initialized = False