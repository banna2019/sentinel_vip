#!/usr/bin/env python
# encoding=utf-8
# Filename: 通过监控Sentinel的主从切换，修改相应的VIP，做到应用连接唯一写IP。

import datetime
import sys
import paramiko
import redis
import os
import psutil
import re
from apscheduler.scheduler import Scheduler

import Sentinel_vip_conf  # 引入配置文件


def start_sentinel(ipaddr, username, passwd, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipaddr, 22, username, passwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        # stdin.write("Y")   #简单交互，输入 ‘Y’
        out = stdout.readlines()
        # 屏幕输出
        for o in out:
            print o,
        print '%s\tOK\n' % (ipaddr)
        ssh.close()
    except:
        print '%s\tError\n' % (ipaddr)


# 获取redis vip 配置情况
def getvip(ipaddr, username, passwd, cmdvip):
    # 判断主机vip 情况，rvip 值为1 则说明有VIP，值为0则说明没有VIP。
    global rvip  # 定义全局变量rvip ，方便方法mip 调用。
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipaddr, 22, username, passwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(cmdvip)
        # stdin.write("Y")   #简单交互，输入 ‘Y’
        out = stdout.readlines()
        # 屏幕输出
        o = out
        rvip = o[0]
        print o[0]
        print '%s\tOK\n' % (ipaddr)
        ssh.close()
    except:
        print '%s\tError\n' % (ipaddr)


# 删除非master redis vip
def delvip(ipaddr, username, passwd, delcmdvip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipaddr, 22, username, passwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(delcmdvip)
        # stdin.write("Y")   #简单交互，输入 ‘Y’
        out = stdout.readlines()
        # 屏幕输出
        print out[0]
        print '%s\tOK\n' % (ipaddr)
        ssh.close()
    except:
        print '%s\tError\n' % (ipaddr)


# 添加master redis vip
def addvip(ipaddr, username, passwd, addcmdvip):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ipaddr, 22, username, passwd, timeout=5)
        stdin, stdout, stderr = ssh.exec_command(addcmdvip)
        # stdin.write("Y")   #简单交互，输入 ‘Y’
        out = stdout.readlines()
        # 屏幕输出
        print out[0]
        print '%s\tOK\n' % (ipaddr)
        ssh.close()
    except:
        print '%s\tError\n' % (ipaddr)


def mip(ipaddr):
    try:
        rs = redis.Redis(host=ipaddr, port=26379)
        rs.ping()

    except Exception, e:
        start_sentinel(ipaddr, username, passwd, cmd)
        info = sys.exc_info()
        print info[0], ":", info[1]
        print "restart %s redis sentinel" % (ipaddr)

    cmdvip = "ip addr | grep %s > /dev/null;if [ $? = 0 ];then echo 1;else echo 0;fi" % (
    vip)  # 判断该主机是否有VIP 1为有VIP，0为没有VIP。
    delcmdvip = "ip addr del %s/24 dev eth0" % (vip)  # 删除VIP
    addcmdvip = "ip addr add %s/24 dev eth0" % (vip)  # 添加VIP

    getvip(ipaddr, username, passwd, cmdvip)

    master_ip = rs.info()
    mip = master_ip['master0']['address'].split(':')[0]
    print mip

    # 判断redis 是主还是从
    if ipaddr == mip:
        print "%s %s redis is master" % (datetime.datetime.now(), ipaddr)
        # 判断master 是否有VIP
        if int(rvip) == 1:
            print "%s master %s redis vip %s" % (datetime.datetime.now(), ipaddr, vip)
        else:
            print "Error %s master %s redis no vip %s" % (datetime.datetime.now(), ipaddr, vip)
            addvip(ipaddr, username, passwd, addcmdvip)
    else:
        print "%s %s redis is slave" % (datetime.datetime.now(), ipaddr)
        # 判断slave 是否有VIP
        if int(rvip) == 1:
            print "Error %s slave %s redis vip %s" % (datetime.datetime.now(), ipaddr, vip)
            delvip(ipaddr, username, passwd, delcmdvip)
        else:
            print "%s slave %s redis no vip %s" % (datetime.datetime.now(), ipaddr, vip)


def main():
    global vip
    global username
    global passwd
    global cmd

    vip = Sentinel_vip_conf.vip
    username = Sentinel_vip_conf.username
    passwd = Sentinel_vip_conf.passwd
    cmd = "%s//redis-sentinel %s" % (
    Sentinel_vip_conf.redis_dir, Sentinel_vip_conf.sentinel_conf)  # 启动redis-sentinel 命令

    for ipaddr in Sentinel_vip_conf.redis_host:
        mip(ipaddr)


if __name__ == '__main__':

    # 禁止重复运行Sentinel_vip.py 进程
    processnum = len(os.popen('ps aux | grep Sentinel_vip.py | grep -v grep | grep -v sh ').readlines())  # 获取运行的进程数量

    if int(processnum) <= 1:
        print processnum
        sched = Scheduler()
        sched.daemonic = False
        sched.add_cron_job(main, day_of_week='*', hour='*', minute='0-59', second='*/3')
        sched.start()

    else:
        print "the number of running process is %s,stop it" % (processnum)
        exit(0)
