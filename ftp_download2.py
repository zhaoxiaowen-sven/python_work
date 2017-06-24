#!/usr/bin/env python
# coding:utf-8

import os
from ftplib import FTP
import time

SAVE_DIR = "trace/"
TARGET_FILE = "atrace"
TIME_STAMP = "%Y%m%d%H%M%S"
HOST = "172.25.105.226"
DIR = "UniversalTest/performance_ScenarioTest/"
bufsize = 1024

def comparetime(time1, time2):
    if time1 - time2 > 0:
        return True
    else:
        return False

def str2stamp(time1, formatter):
    return time.mktime(time.strptime(time1, formatter))

def ftp_download2():
    print("ftp download")
    # 连接ftp目录
    ftp = FTP()
    ftp.set_debuglevel(0)
    ftp.connect(HOST)
    ftp.login("", "")
    ftp.cwd(DIR)
    dirs = ftp.nlst()
    # print dirs

    # 解析测试用例的父目录,将需要保存的目录下载到本地
    target_dirs = []
    for dirname in dirs:
        # print dirname
        if dirname.startswith("out"):
            arr = dirname.split("-")
            # print arr
            if len(arr) == 3:
                device = arr[1]
                time1 = str2stamp("20" + arr[2], TIME_STAMP)
                start_time = str2stamp("20170524201100", TIME_STAMP)
                # print device , start_time
                if comparetime(time1, start_time):  # start_time特定时间之后的
                    target_dirs.append(dirname)

    print(target_dirs)
    traces = []
    for target_dir in target_dirs:
        # print "target_dir", len(target_dirs)
        dirs = ftp.nlst(target_dir)
        # print "arr = ", arr, len(arr)
        for dir in dirs:
            if (dir.startswith("2017")):
                arr2 = ftp.nlst(target_dir + "/" + dir)
                # print "arr2 = ", len(arr2)
                trace = target_dir + "/" + dir + "/"
                if (trace+TARGET_FILE in arr2):
                    traces.append(trace)
                    # # print "here"
    print(traces)
    for trace in traces:
        try:
            local_path = SAVE_DIR + trace
            if not os.path.exists(local_path):
                os.makedirs(local_path)
            f = open(local_path + TARGET_FILE, "wb")
            server_path = 'RETR ' + trace +TARGET_FILE
            # print "local_path = ",local_path , "server_path",server_path
            ftp.retrbinary(server_path, f.write, bufsize)
            f.close()
        except Exception as e:
            print("read " + trace + " error = ", e)
            continue
    print(traces)
    # ftp.quit()


ftp_download2()
