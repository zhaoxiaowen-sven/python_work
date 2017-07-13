#!/usr/bin/env python
# coding:utf-8
import datetime
import os

from utils.config_utils import ConfigUtils

REPORT_DIR = "D:/PycharmProjects/untitled/report/"

caseMaps, appMaps, deviceMaps = ConfigUtils.readConfig()
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
time_stamp2 = datetime.datetime.now().strftime("%Y-%m-%d")
# coding:utf-8

import numpy as np

# from numpy import *

# data = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
# data = np.array([[1.3, 2.4, 3], [4, 5, 6], [7, 8, 9]])
#
# print(data.astype(np.int32))
# print(data.shape)
#
# print(data.dtype)
#
# zero = np.zeros((2, 10), np.float64)
# print(zero)
#
# one = np.ones((3, 3), int)
# print(one)
#
# em = np.empty((2, 2))
# print(em)
#
# a = np.arange(15)
# print(a)
#
# num_str = np.array([1.1, 1.2])
# print(num_str.astype(np.str_), num_str.shape)
#
# num_str = np.array(['a', 'ab'], dtype=np.string_)
# print(num_str)
#
#
# data = np.array([[1, 2, 3], [4, 5, 6]])
#
# print(data * data)
#
# arr = list([1,2,3,4,5])
# print(arr)
#
# arr[2:] = [5,5]
#
# print(arr)
#
# pids = {'13349': 'com.sina.weibo', '13392': 'wdaemon', '13408': 'com.sina.weibo:remote', '13475': 'com.sina.weibo.image', '13671': 'com.sina.weibo.imageservant'}
#
# for pid in pids:
#     print(pid)

# data = np.random.rand(7, 4)
# print(data)

# t = (1,2,3,2)
# print(t)

# arr = np.random.rand(7)*5

# print(arr)

# print(np.modf(arr))

# arr = np.random.rand(4, 4)


# arr3 = np.array([1,1,2,3,3])
# print(np.unique(arr3))

# np.save('some_array', arr3)


# print(np.load('some_array.npy'))

# arr1 = np.random.randint(0,2,size=100)

# print(arr1)

# arr12 = np.where(arr1>0,1,-1)

# print(arr12)
# arr2 = arr12.cumsum()
# print(arr2)

# print(arr2.min())

# print(arr2.max())

# result = {'count':1, "d":{}}

# count = result.get('count')
# count = 2
# result['count'] += 1
#
# print(result.get('count'))
#
# d = result.get('d')
# d['x'] = 1
# print(result.get('d'))
# anr_path = (anr.split("autotest/")[1]).replace("/","").strip().split("anr")[0]
#
# if not os.path.exists(temp):
#     os.makedirs(temp)
# shutil.copy(anr,temp)
print("===anr end ===")

# np.mean()
import re
PSS_PATTERN = r"(.*)\s+\d+\s+\d+ I am_pss  : \[\d+,\d+,([^,]+),(\d+),(\d+)(,\d+)?\]"
s = "06-05 17:21:16.107  3093  3629 I am_pss  : [10303,10063,com.iqoo.secure,9591808,6098944,0]"
s2 = "07-03 09:49:02.470  1319  1341 I am_pss  : [28230,10144,com.tencent.androidqqmail,43467776,38531072]"
match_pss = re.search(PSS_PATTERN, s)

s3 = "06-05 17:20:41.243  3093  4830 I am_kill : [0,7680,com.volte.config,906,empty #17]"

# if match_pss:
#     print("111")
#     time = match_pss.group(1)
#     process = match_pss.group(2)
#     pss = match_pss.group(3)
#     vss = match_pss.group(4)
#     print(time, process, pss, vss)

# KILL_PATTERN = r"(.*)\s+\d+\s+\d+ I am_kill : \[\d+,\d+,([^,]+),(\d+),.*\]"
# s4 = "07-02 20:38:53.104  1319  2385 I am_kill : [0,1960,com.android.externalstorage,15,empty #31]"
# match_kill = re.search(KILL_PATTERN, s4)
# if match_kill:
#     print(222)
#     time = match_kill.group(1)
#     process = match_kill.group(2)
#     oom_adj = match_kill.group(3)
#     print(time, process, oom_adj)
s5 = "06-05 17:53:43.939  3093  3629 I am_meminfo: [323739648,114036736,0,330731520,259238912]"
MEM_PATTERN = r"(.*)\s+\d+\s+\d+ I am_meminfo: \[(\d+),(\d+),(\d+),(\d+),(\d+)\]"
match_mem = re.search(MEM_PATTERN, s5)
if match_mem:
    print(222)
    time = match_mem.group(1)
    cached = match_mem.group(2)
    free = match_mem.group(3)
    zram = match_mem.group(4)
    kernel = match_mem.group(5)
    native = match_mem.group(6)
    print(cached, free, zram, kernel, native)