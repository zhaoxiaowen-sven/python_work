#!/usr/bin/env python
# coding:utf-8
import datetime

from utils.config_utils import ConfigUtils

REPORT_DIR = "D:/PycharmProjects/untitled/report/"

caseMaps, appMaps, deviceMaps = ConfigUtils.readConfig()
time_stamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
time_stamp2 = datetime.datetime.now().strftime("%Y-%m-%d")

from pandas import DataFrame,Series
import pandas as pd
import numpy as np

# coding:utf-8

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
# s5 = "06-05 17:53:43.939  3093  3629 I am_meminfo: [323739648,114036736,0,330731520,259238912]"
# MEM_PATTERN = r"(.*)\s+\d+\s+\d+ I am_meminfo: \[(\d+),(\d+),(\d+),(\d+),(\d+)\]"
# match_mem = re.search(MEM_PATTERN, s5)
# if match_mem:
#     print(222)
#     time = match_mem.group(1)
#     cached = match_mem.group(2)
#     free = match_mem.group(3)
#     zram = match_mem.group(4)
#     kernel = match_mem.group(5)
#     native = match_mem.group(6)
#     print(float(cached)+float(free))
#     print(cached, free, zram, kernel, native)
# line = "#07-13 09:29:24.014  1423 15264 D VivoPerfService: 1030_3: com.jingdong.app.mall/.MainFrameActivity#31#14963#com.jingdong.app.mall"
# pattern = r"(.*)\s+\d+\s+\d+ D VivoPerfService: 1030_3: (\S+)#(\d+)#(\d+)#(\S+)"
# if line.find("VivoPerfService") != -1:
#     match_obj = re.search(pattern, line)
#     if match_obj:
#         time = match_obj.group(1)
#         process = match_obj.group(2)
#         frame = match_obj.group(3)
#         pkg = match_obj.group(5)
#         print(time, process, frame, pkg)

# d = {"a":[1]}
# d.get('a').append(1)
# print(d)

# li=[(2,'a'),(4,'b'),(1,'d')]
# li.sort()
# print(li)

# ANR_PATTERN = "(.*)\s+\d+\s+\d+ I am_anr\s+:\s+\[(\d+,){2}(.*),\d+,.*\]"
# line = "06-05 22:53:40.279  3093  3632 I am_anr  : [0,26110,com.tencent.mm,951598660,Broadcast of Intent { act=com.tencent.mm.plugin.report.service.KVCommCrossProcessReceiver flg=0x10 cmp=com.tencent.mm/.plugin.report.service.KVCommCrossProcessReceiver (has extras) }]"
# match_anr = re.search(ANR_PATTERN, line)
# if match_anr:
#     print("1111")
#     time = match_anr.group(1)
#     time = time[6:-5]
#     pkgname = match_anr.group(3)
#     print(pkgname)
import matplotlib.pyplot as plt
import pandas
import numpy as np
from pandas import DataFrame,Series
# print(np.random.randn(1000).cumsum())
# fig = plt.figure()
# ax1 = fig.add_subplot(2, 2, 1)
# ax2 = fig.add_subplot(2, 2, 2)
# ax3 = fig.add_subplot(2,2,3)
#
# # _ = ax1.hist(randn(100), bins=20, color='k')
# ax2.scatter(np.arange(30),np.arange(30) * randn(30))
# plt.plot(randn(50).cumsum(), 'g', '-o')
# # plt.plot
# # plt.subplots(2, 3)
# plt.show()
# plt.plot(randn(50).cumsum(),'k--')
# df = pandas.DataFrame({"var1": [1, 2, 3, 4, 5, 6], "var2": [1, 2, 3, 4, 5, 6]})
# plt.plot(df["var1"], df["var2"], linestyle='--', marker='o', color='r')
# plt.xticks([x for x in range(10)])
# plt.xlim([0, 10])
# plt.ylim([0, 10])
# plt.legend(loc="best")
# # plt.text
# plt.show()

# df = DataFrame(np.random.randn(10,4).cumsum(0),columns=['A','B','C','D'],index=np.arange(0,100,10))
# df.plot().show()

# 07-19 09:55:52.497  1449  2172 I battery_level: [95,4207,317]
# BATTERY_PATTERN = r'(.*)\s+\d+\s+\d+ I battery_level: \[(\d+),(\d+),(\d+)\]'
# line = "07-19 09:55:52.497  1449  2172 I battery_level: [95,4207,317]"
# match_battery = re.search(BATTERY_PATTERN, line)
# if match_battery:
#     time = match_battery.group(1)
#     level = match_battery.group(2)
#     voltage = match_battery.group(3)
#     T = match_battery.group(4)
#
#     print(time, level, voltage, T)

# coding: utf-8
# coding: utf-8

# import matplotlib.pyplot as plt
# import numpy as np
#
# y = np.random.randint(0,100,100)
# X = [i for i in range(100)]
#
# X_ticks = []
# for i in range(1,101):
#     if i % 50==0 or i==100:
#         X_ticks.append(str(i))
#     else:
#         X_ticks.append('')
#
# plt.xticks(X,X_ticks)
# plt.plot(X,y,'r')
#
# plt.show()

# line = "11-02 16:12:32.620  1344  1512 I am_activity_launch_time: [0,111304510,com.bbk.appstore/.ui.AppStore,437,437]"
# pattern = r"(.*)\s+\d+\s+\d+ I am_activity_launch_time:\s+\[\d+,\d+,(.*),(\d+),(\d+)\]"
# match_obj = re.search(pattern, line)
# if match_obj:
#     time = match_obj.group(1)
#     ui = match_obj.group(2)
#     launch = match_obj.group(3)
#     total = match_obj.group(4)
#     print(time, ui, launch, total)


import sqlite3
conn = sqlite3.connect("resume.db")
cur = conn.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS resume (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        imei text,
        time text,
        pkg text
    )
    ''')

df = DataFrame(data=np.arange(12).reshape(4,3),columns=['imei', 'time', 'pkg'])
print(df)
df.to_sql("resume", conn, index=False, if_exists="append")