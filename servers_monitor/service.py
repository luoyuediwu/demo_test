#!/usr/bin/env python
# -*- coding: utf-8 -*-
__version__ = '1.0.0.0'

"""
@brief 简介 
@details 详细信息
@author  luoyuediwu
@data    2016-01-06 
"""
import os
import signal
import eventlet
from oslo_config import cfg
from oslo_log import log
import oslo_messaging as messaging
from oslo_messaging import Target
from oslo_service import service as os_service

import single_instance

cfg_opts = [
    cfg.StrOpt('action', default='start'),
    cfg.BoolOpt('multi_process', default=False, help='whether allow to run multi process')
]

cfg.CONF.register_cli_opts(cfg_opts)

__name__ = globals().get('__name__')
#__file__ = os.path.join(os.environ['INSTALL_PATH'], __name__.replace('.', '/') + '.py')
LOG = log.getLogger(__name__)

class ServiceSignal(object):
    """ServiceSignal"""

    import sys
    if sys.platform == 'win32':
        SIG_START = signal.SIGILL
        SIG_STOP = signal.SIGTERM
        SIG_HANGUP = signal.SIGINT
    else:
        SIG_START = signal.SIGRTMIN + 1
        SIG_STOP = signal.SIGRTMIN + 2
        SIG_HANGUP = signal.SIGRTMIN + 3

    @classmethod
    def get_signal_by_action(cls, action):
        """
        根据命令参数获取信号值
        """
        if action == 'start':
            return cls.SIG_START
        elif action == 'stop':
            return cls.SIG_STOP
        elif action == 'hangup':
            return cls.SIG_HANGUP
        else:
            return None

class Service(object):
    """
    ServiceBase
    """
    def __init__(self, topic, server_name, endpoint, exchange='service_manage', executor='blocking', srv_mng_url=None):
        super(Service,self).__init__()
        self._topic = topic
        self._server_name = server_name
        self._exchange = exchange
        self._executor = executor
        self.srv_mng_url = srv_mng_url

        self._target = Target(exchange=self._exchange,topic=self._topic,server=self._server_name)
        self._transport = messaging.get_transport(cfg.CONF,srv_mng_url)
        self._server = None
        self._launcher = None

        self._listener = None
        self.endpoint = endpoint
        self.running = True

        self.single_instance = single_instance.SingleInstance('{0}_instance'.format(server_name))

        signal.signal(ServiceSignal.SIG_START, self.on_signal)
        signal.signal(ServiceSignal.SIG_STOP, self.on_signal)
        signal.signal(ServiceSignal.SIG_HANGUP, self.on_signal)
        LOG.info('{0} constructor'.format(self._server_name))

    def check_cli_params(self):
        """
        初始化Service,检查命令参数，决定服务启动模式
        :return:
        """
        LOG.info('{0} check_cli_params'.format(self._server_name))
        if not cfg.CONF.multi_process:
            # 不允许多进程模式，只能单实例运行
            if not self.single_instance.lock_instance():
                # 锁定失败，表明已有运行的实例，则需要
                LOG.warn('{0} lock exist, need to run as command client'.format(self._server_name))
                self._run_as_command_client()
                return False
            else:
                self.single_instance.write_pid_to_file()
        LOG.warn('{0} lock does not exist, need to run as server'.format(self._server_name))
        return True

    def _run_as_command_client(self):
        """
        以命令行客户端模式运行，将命令行参数通过connection传递给以运行的实例
        :return:
        """
        try:
            pid = self.single_instance.read_pid_from_file()
            cmd_signal = ServiceSignal.get_signal_by_action(cfg.CONF.action)
            if pid and cmd_signal:
                os.kill(pid, cmd_signal)
        except Exception as err:
            LOG.exception(err)

    def start(self):
        """
        启动服务
        :return:
        """
        if self._start_endpoint():
            endpoints = [self.endpoint]
            print(self._transport,self._target,endpoints,self._executor)
            self._server = messaging.get_rpc_server(self._transport, self._target, endpoints, executor=self._executor)
            self._launcher = os_service.launch(cfg.CONF, self._server)
            return True
        else:
            return False

    def stop(self):
        """
        停止服务
        :return:
        """
        self._stop_endpoint()
        if self._launcher:
            self._launcher.stop()

    def _start_endpoint(self):
        if self.endpoint and self.running:
            if self.endpoint.init_endpoint():
                self.endpoint.start_endpoint()
                self.running = True
                print "testsdfsdf"
                return True
            else:
                self.stop()
        return False

    def _stop_endpoint(self):
        if self.endpoint and self.running:
            self.endpoint.stop_endpoint()
        self.running = False

    def free(self):
        """
        释放资源
        :return:
        """
        self.single_instance.free_instance()

    def wait(self):
        """
        等待服务退出
        :return:
        """
        self._launcher.wait()

    def on_signal(self,signum,frame):
        """
        信号回调，处理信号信息
        :param signum:
        :param frame:
        :return:
        """
        LOG.warn('{0} receive signal {1}'.format(self._server_name, signum))
        if signum == ServiceSignal.SIG_START:
            LOG.warn('{0} receive start signal'.format(self._server_name))
            eventlet.spawn(self._start_endpoint)
            # self._start_endpoint()
        elif signum == ServiceSignal.SIG_STOP:
            LOG.warn('{0} receive stop signal'.format(self._server_name))
            eventlet.spawn(self.stop)
            # self.stop()
        elif signum == ServiceSignal.SIG_HANGUP:
            LOG.warn('{0} receive hangup signal'.format(self._server_name))
            eventlet.spawn(self._stop_endpoint)
            # self._stop_endpoint()


class Services(object):
    """
    ServicesBase
    """

    def __init__(self, server_name):
        super(Services, self).__init__()
        self._server_name = server_name
        self._launcher = os_service.ServiceLauncher(cfg.CONF)
        self.running = False
        self._services = []

        self.single_instance = single_instance.SingleInstance('{0}_instance'.format(server_name))

        signal.signal(ServiceSignal.SIG_START, self.on_signal)
        signal.signal(ServiceSignal.SIG_STOP, self.on_signal)
        signal.signal(ServiceSignal.SIG_HANGUP, self.on_signal)
        LOG.info('{0} constructor'.format(self._server_name))


    def add_service(self, topic, server, endpoint):
        self._services.append({
            "topic": topic,
            "server": server,
            "endpoint": endpoint
        })

    def _launch_service(self, topic, server, endpoint, exchange='service_manage', srv_mng_url=None):
        """
        启动RPC服务
        """
        _target = Target(exchange=exchange, topic=topic, server=server)
        _transport = messaging.get_transport(cfg.CONF, srv_mng_url)
        _server = messaging.get_rpc_server(_transport, _target, endpoint)
        self._launcher.launch_service(_server)

    def check_cli_params(self):
        """
        初始化Service，检查命令参数，决定服务启动模式
        @return:
        """
        LOG.info('{0} check_cli_params'.format(self._server_name))
        if not cfg.CONF.multi_process:
            # 不允许多进程模式，只能单实例运行
            if not self.single_instance.lock_instance():
                # 锁定失败，表明已有运行的实例，则需要
                LOG.warn('{0} lock exist, need to run as command client'.format(self._server_name))
                self._run_as_command_client()
                return False
            else:
                self.single_instance.write_pid_to_file()
        LOG.warn('{0} lock does not exist, need to run as server'.format(self._server_name))
        return True

    def _run_as_command_client(self):
        """
        以命令行客户端模式运行，将命令行参数通过connection传递给以运行的实例
        """
        try:
            pid = self.single_instance.read_pid_from_file()
            cmd_signal = ServiceSignal.get_signal_by_action(cfg.CONF.action)
            if pid and cmd_signal:
                os.kill(pid, cmd_signal)
        except Exception as err:
            LOG.exception(err)

    def start(self):
        """
        启动服务
        @return:
        """
        if self._start_endpoint():
            for server in self._services:
                self._launch_service(topic=server['topic'],
                                     server=server['server'],
                                     endpoint=server['endpoint'])
            return True
        else:
            return False

    def stop(self):
        """
        停止服务
        @return:
        """
        self._stop_endpoint()
        if self._launcher:
            self._launcher.stop()

    def _stop_endpoint(self):
        if len(self._services) and self.running:
            for server in self._services:
                endpoint = server['endpoint']
                if endpoint:
                    endpoint.stop_endpoint()
        self.running = False

    def _start_endpoint(self):
        if len(self._services) and not self.running:
            for server in self._services:
                endpoint = server['endpoint']
                if endpoint:
                    if endpoint.init_endpoint():
                        endpoint.start_endpoint()
                    else:
                        return False
            self.running = True
            return True
        return False


    def free(self):
        """
        释放资源
        """
        self.single_instance.free_instance()

    def wait(self):
        """
        等待服务退出
        @return:
        """
        self._launcher.wait()

    def on_signal(self, signum, frame):
        """
        信号回调，处理信号信息
        @param signum:
        @param frame:
        @return:
        """
        LOG.warn('{0} receive signal {1}'.format(self._server_name, signum))
        if signum == ServiceSignal.SIG_START:
            LOG.warn('{0} receive start signal'.format(self._server_name))
            eventlet.spawn(self._start_endpoint)
            # self._start_endpoint()
        elif signum == ServiceSignal.SIG_STOP:
            LOG.warn('{0} receive stop signal'.format(self._server_name))
            eventlet.spawn(self.stop)
            # self.stop()
        elif signum == ServiceSignal.SIG_HANGUP:
            LOG.warn('{0} receive hangup signal'.format(self._server_name))
            eventlet.spawn(self._stop_endpoint)
            # self._stop_endpoint()


class CommonService(object):
    pass






