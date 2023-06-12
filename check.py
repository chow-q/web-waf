#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import datetime
from datetime import timedelta
from dateutil import parser

# 获取当前系统时间
current_time = datetime.datetime.now()
# 定义需要过滤的URL,需要忽略的url
filter_urls = ["/fen1.jpg", "/favicon.ico"]
#符合规则的ip出现的次数，如果大于该值，就添加到黑名单：
count=5
# 计算5分钟之前的时间，每次运行获取的日志的时间段
past_time = current_time - timedelta(minutes=5)

# 定义存储IP的字典
ip_dict = {}
#running log
run_log = "D:/BtSoft/apache/conf/run_log.txt"
# 循环历遍D盘下的所有access.log结尾的文件
log_dir = "D:\\BtSoft\\wwwlogs"
for file in os.listdir(log_dir):
    if file.endswith("access.log"):
      log_file = os.path.join(log_dir, file)
      print(log_file)
      # 打开日志文件，取最新的1000行日志进行处理，查找状态码为404的IP，并记录到字典中
      with open(log_file, "r") as f:
        lines = f.readlines()[-1000:]
        for line in lines:
            # 判断URL是否需要过滤
            need_filter = False
            for url in filter_urls:
                if url in line:
                    need_filter = True
                    break
            if need_filter:
                continue
            log_time_str = re.search(r"\[(.*?)\]", line).group(1)
            log_time_naive = parser.parse(log_time_str.replace(":", " ", 1))
            # 把offset-aware的datetime转换为offset-naive的datetime
            log_time = log_time_naive.replace(tzinfo=None)
            if " 404 " in line and log_time >= past_time:
                print(line)
                with open(run_log, "r+") as f:
                    f.write("%s\n" % line)
                match_obj = re.search(r"\d+\.\d+\.\d+\.\d+", line)
                if match_obj:
                    ip = match_obj.group()
                    if ip in ip_dict:
                        ip_dict[ip] += 1
                    else:
                        ip_dict[ip] = 1

# 添加需要拦截的IP到deny列表中
deny_file = "D:/BtSoft/apache/conf/deny.conf"  # 请根据实际情况修改文件路径

deny_status = False
with open(deny_file, "r+") as f:
    content = f.read()
    print(ip_dict)
    for ip in ip_dict:
        #如果404ip出现的次数大于1，并且不在黑名单中，就添加到黑名单
        if ip_dict[ip] > count and ip not in content:
            f.write("Deny from %s\n" % ip)
            print("IP %s is add" % ip)
            deny_status = True
    if deny_status:
            # 重新加载Apache配置
            os.system("net stop apache & net start apache")  # 请根据实际情况修改命令路径

