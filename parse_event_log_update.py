#!/usr/bin/env python
# coding:utf-8

__author = 'zhaoxiaowen'
import re
import threading
import time
from collections import Counter

import xlsxwriter
import xlsxwriter.utility as utility
import time
import datetime
from dateutil.parser import parse

TIME_STAMP = "%m-%d %H:%M:%S.%f"

DIR = "E:/Project/Pycharm/ftp_work/event/events_log"
START_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_start: \[(\d+,){3}(.*),(.*),.*\]"
BOUND_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_bound: \[(\d+,){2}(.*)\]"


def comparetime(time1, time2):
    return (parse(time2) - parse(time1)).total_seconds() * 1000
    # time.mktime(time.strptime(time1, TIME_STAMP))


def parse_proc():
    proc_dict = {}
    with open(DIR, encoding="utf-8") as f:
        while True:
            line = f.readline()
            # print index
            match_start = re.search(START_PATTERN, line)
            if match_start:
                # 找到start_proc的地方,比较位置
                index = f.tell()
                # print(index)
                timestr1 = match_start.group(1)
                procname1 = match_start.group(3)
                type = match_start.group(4)
                # print 'match_start', timestr, procname, type
                # print 'timestr1', timestr1
                # 连续读10行，找到bound的标记
                for x in range(10):
                    line2 = f.readline()

                    match_bound = re.search(BOUND_PATTERN, line2)
                    if match_bound:
                        timestr2 = match_bound.group(1)
                        procname2 = match_bound.group(3)
                        # print procname2, timestr1
                        if procname2 == procname1:  # and len(timestr1) == len(timestr2):
                            # if procname2 == "com.android.bluetooth":
                            # print "======", timestr1, timestr2
                            try:
                                tmp = comparetime(timestr1, timestr2)
                                if procname2 in proc_dict.keys():
                                    l = proc_dict.get(procname2)
                                    l[1].append(timestr1)
                                    l[0].append(tmp)
                                else:
                                    proc_dict[procname2] = [[tmp],[timestr1]]
                                    break
                            except Exception as e:
                                print(e, procname2, timestr1, timestr2)
                                # print line
                                # print line2
                                # flag = 1
                                break

                f.seek(index, 0)
            if not line: break
        return proc_dict

proc_dict = parse1()
wb = xlsxwriter.Workbook("proc.xlsx")
sheet = wb.add_worksheet("proc_start_time")
i = 0
for k, v in proc_dict.items():
    sheet.write(i, 0, k)
    for x in range(len(v[0])):
        sheet.write(i, x + 1, v[0][x])
    i += 1
wb.close()

# def parse2():
#     proc_dict = {"start": {}, "bound": {}}
#     start = proc_dict.get("start")
#     bound = proc_dict.get("bound")
#     with open(DIR) as f:
#         for line in f:
#             match_start = re.search(START_PATTERN, line)
#             match_bound = re.search(BOUND_PATTERN, line)
#             if match_start:
#                 timestr1 = match_start.group(1).strip()
#                 procname1 = match_start.group(3)
#                 if procname1 in start.keys():
#                     start.get(procname1).append(timestr1)
#                 else:
#                     start[procname1] = [timestr1]
#             elif match_bound:
#                 timestr2 = match_bound.group(1).strip()
#                 procname2 = match_bound.group(3)
#                 if procname2 in bound.keys():
#                     bound.get(procname2).append(timestr2)
#                 else:
#                     bound[procname2] = [timestr2]
#             else:
#                 pass
#     print(proc_dict)
#
#     results_dict = {}
#     for x in start.keys():
#         v1 = start.get(x)
#         print(x, len(v1))
#         v2 = bound.get(x)
#
#         length = len(v2) if len(v2) < len(v1) else len(v1)
#         if v2 is not None:
#             results_dict[x] = []
#             for i in range(length):
#                 results_dict[x].append(comparetime(v1[i], v2[i]))
#                 # print x, len(v2)
#
#     print(results_dict)
#     wb = xlsxwriter.Workbook("proc.xlsx")
#     sheet = wb.add_worksheet("proc_start_time")
#     i = 0
#     for k, v in results_dict.items():
#         sheet.write(i, 0, k)
#         for x in range(len(v)):
#             sheet.write(i, x + 1, v[x])
#         i += 1
#     wb.close()



# results_dict = parse2()
# parse1()
# for k, v in proc_dict.items():
#     print v[0]
#     print v[1]


# print proc_dict
