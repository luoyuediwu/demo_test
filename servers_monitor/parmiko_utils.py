#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/3 9:59
# @Author  : luoyuediwu
# @Site    : 
# @File    : parmiko_utils.py
# @Software: PyCharm
import paramiko
import ConfigParser
import os
from stat import *

class ParmikoUtils(object):

    def __init__(self,conf_name):
        self.ssh = paramiko.SSHClient()
        self.conf_name  = conf_name
        self.trans = []
        self.server_info = []

    def get_ip_port(self):
        cf = ConfigParser.ConfigParser()
        cf.read(self.conf_name)
        s = cf.sections()
        ip_infos = list()
        for section in s:
            ip_info = dict()
            ip_info['host'] = cf.get(section,"host")
            ip_info['port'] = cf.getint(section,"port")
            ip_info['user'] = cf.get(section,"user")
            ip_info['passwd'] = cf.get(section,"pass")
            ip_infos.append(ip_info)
        return ip_infos

    def get_trans(self):
        for ip_info in self.get_ip_port():
           trans_info = dict()
           trans = paramiko.Transport((ip_info['host'],ip_info['port']))
           trans.connect(username=ip_info['user'],password=ip_info['passwd'])
           trans_info["tran"] = trans
           trans_info["ip_info"] = ip_info
           self.trans.append(trans_info)

    def do_cmds(self,cmds=list()):
        for tran in self.trans:
            self.ssh._transport = tran["tran"]
            for cmd in cmds:
                stdin, stdout, stderr = self.ssh.exec_command(cmd)
                print(stdout.read())

    def __get_all_files_in_local_dir(self, local_dir):
        # 保存所有文件的列表
        all_files = list()
        # 获取当前指定目录下的所有目录及文件，包含属性值
        files = os.listdir(local_dir)
        for x in files:
            # local_dir目录中每一个文件或目录的完整路径
            filename = os.path.join(local_dir, x)
            # 如果是目录，则递归处理该目录
            if os.path.isdir(x):
                all_files.extend(self.__get_all_files_in_local_dir(filename))
            else:
                all_files.append(filename)
        return all_files

    def __get_all_files_in_remote_dir(self, sftp, remote_dir):
        # 保存所有文件的列表
        all_files = list()
        # 去掉路径字符串最后的字符'/'，如果有的话
        if remote_dir[-1] == '/':
            remote_dir = remote_dir[0:-1]
        # 获取当前指定目录下的所有目录及文件，包含属性值
        files = sftp.listdir_attr(remote_dir)
        for x in files:
            # remote_dir目录中每一个文件或目录的完整路径
            filename = remote_dir + '/' + x.filename
            # 如果是目录，则递归处理该目录，这里用到了stat库中的S_ISDIR方法，与linux中的宏的名字完全一致
            if S_ISDIR(x.st_mode):
                all_files.extend(self.__get_all_files_in_remote_dir(sftp, filename))
            else:
                all_files.append(filename)
        return all_files

    def upload_files(self,local_dir,remote_dir):
        for tran in self.trans:
            sftp = paramiko.SFTPClient.from_transport(tran['tran'])
            # 去掉路径字符穿最后的字符'/'，如果有的话
            if remote_dir[-1] == '/':
                remote_dir = remote_dir[0:-1]
            # 获取本地指定目录及其子目录下的所有文件
            all_files = self.__get_all_files_in_local_dir(local_dir)
            # 依次put每一个文件
            for x in all_files:
                filename = os.path.split(x)[-1]
                remote_filename = remote_dir + '/' + filename
                print u'Put文件%s传输中...' % filename
                sftp.put(x, remote_filename)

    def down_files(self,local_dir,remote_dir):
        for tran in self.trans:
            sftp = paramiko.SFTPClient.from_transport(tran['tran'])
            all_files = self.__get_all_files_in_remote_dir(sftp, remote_dir)
            # 依次get每一个文件
            for x in all_files:
                filename = x.split('/')[-1]
                local_filename = os.path.join(local_dir, filename)
                print u'Get文件%s传输中...' % filename
                sftp.get(x, local_filename)

    def sftp_get(self, remotefile, localfile):
        for tran in self.trans:
            sftp = paramiko.SFTPClient.from_transport(tran['tran'])
            sftp.get(remotefile, localfile)

    # put单个文件
    def sftp_put(self, localfile, remotefile):
        for tran in self.trans:
            sftp = paramiko.SFTPClient.from_transport(tran['tran'])
            sftp.put(remotefile, localfile)


    def get_file_resources(self):
        for tran in self.trans:
            server_info = {}
            self.ssh._transport = tran["tran"]
            #查看文件资源
            cmd = "df -h|sed '1d'|awk '{print $1\",\" $2\",\" $3\",\" $4\",\" $5\",\"$6}'"
            stdin, stdout, stderr = self.ssh.exec_command(cmd)
            filesystem_usage = stdout.readlines()
            server_info['file_res'] = filesystem_usage
            chk = "date \"+%Y-%m-%d %H:%M:%S\""
            stdin, stdout, stderr = self.ssh.exec_command(chk)
            check_time = stdout.readlines()
            check_time = check_time[0]
            server_info['check_time'] = check_time
            cpu = "vmstat 1 3|sed  '1d'|sed  '1d'|awk '{print $15}'"
            stdin, stdout, stderr = self.ssh.exec_command(cpu)
            cpu = stdout.readlines()
            cpu_usage = str(round((100 - (int(cpu[0]) + int(cpu[1]) + int(cpu[2])) / 3), 2)) + '%'
            server_info['cpu_usage'] = cpu_usage
            mem = "cat /proc/meminfo|sed -n '1,4p'|awk '{print $2}'"
            stdin, stdout, stderr = self.ssh.exec_command(mem)
            mem = stdout.readlines()
            mem_total = round(int(mem[0]) / 1024)
            mem_total_free = round(int(mem[1]) / 1024) + round(int(mem[2]) / 1024) + round(int(mem[3]) / 1024)
            mem_usage = str(round(((mem_total - mem_total_free) / mem_total) * 100, 2)) + "%"
            server_info['meory_usage'] = mem_usage
            self.server_info.append(server_info)

if __name__ == "__main__":
    putil = ParmikoUtils('tools.conf')
    putil.get_trans()
    #putil.do_cmds(['ls -ll','monit summary'])
    putil.get_file_resources()
    # putil.down_files(r'C:\11',r'/root/test/')
    putil.server_info


