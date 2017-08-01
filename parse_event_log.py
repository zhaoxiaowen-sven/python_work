#!/usr/bin/env python
# coding:utf-8

SCREEN_REPORT = "event_log_screen_results.xlsx"
EXCEPT_REPORT = "event_log_except_results.xlsx"
PROC_REPORT = "event_log_proc_results.xlsx"
RESUME_REPORT = "event_log_resume_results.xlsx"
PSS_REPORT = "event_log_pss_results.xlsx"
KILL_REPORT = "event_log_kill_results.xlsx"
MEM_REPORT = "event_log_mem_results.xlsx"
BATTERY_REPORT = "event_log_battery_results.xlsx"

MB = 1024.0 * 1024.0

__author = 'zhaoxiaowen'
import datetime
import os
import threading
import time
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xlsxwriter
import xlsxwriter.utility as utility
from pandas import DataFrame

from event_parser.parsers import *

# DIR = "E:/Project/Pycharm/ftp_work/event/"
DIR = "D:/log/eventlog/PD1610/"
DIR3 = "D:/log/eventlog/PD1619/"
DIR2 = "E:/Project/Pycharm/ftp_work/event/"

# DIR = "D:/log2/eventlog/862668030011416/"
REPORT_PATH = "E:/Project/Pycharm/ftp_work/event_report/"

HOUR = 60 * 60 * 1000.0


class ParseThread(threading.Thread):
    def __init__(self, func, args, threadid=0, name=''):
        threading.Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        self.func(*self.args)


class EventLog:
    def __init__(self, path, prefix_name):
        # print("init")
        self.path = path
        self.prefix_name = prefix_name

    def parse(self, rev=True):
        start_time = time.time()
        results = self.parse_files()
        # print("pss", results.get('pss'))
        end_time = time.time() - start_time
        print("parse files end %.1f s" % end_time)
        # print(results)
        # print results.get("screen").keys()
        # for k, v in results.get("screen").items():
        #     print(k, v)
        self.make_sheets(results, self.prefix_name)

    def comparetime(self, time1, time2):
        return (parse(time2) - parse(time1)).total_seconds() * 1000

    def parse_files(self):
        results = {'count_time': 0,
                   'resume': {},
                   'resume2': {"time": [], "ui": [], "interval": []},
                   'resume3': {"time": [], "pkg": []},  # resume 的所有记录
                   'resume4': {"time": [], "pkg": []},  # 灭屏的数据
                   'resume_called': {"time": [], "pkg": []},
                   'crash': {}, 'anr': {},
                   'screen': {},
                   "proc": {},
                   "proc_start": {},
                   "screen_focused": {"count": 1}, 'pss': {}, "kill": {},
                   "mem": {"time": [], "cached": [], "free": [], "zram": [], "kernel": [], "native": []},
                   "battery": {"time": [], "level": [], "voltage": [], "T": []},
                   "launch": {"time": [], "ui": [], "start": [], "total": []}
                   }
        filepaths = []
        for dirpath, dirnames, filenames in os.walk(self.path):
            for file in filenames:
                filepaths.append(os.path.join(dirpath, file))
        # print(filepaths)
        for p in filepaths:
            print("======", p, "======")
            self.parse_file(p, results)  # result[] = temp

        return results

    def parse_file(self, path, result):
        # temp_resume = result.get('resume')
        # temp_crash = result.get("crash")
        # temp_anr = result.get('anr')
        # temp_proc = result.get("proc")
        # temp_screen = result.get("screen")
        # temp_screen_focused = result.get("screen_focused")
        # temp_pss = result.get("pss")
        # count_time = result.get('count_time')
        # print("****", count_time)
        # 多个路径 这里加循环 for path in paths:
        with open(path, encoding="utf-8") as f:
            # while True:

            lines = f.readlines()
            length = len(lines)
            try:
                first_line = lines[0]
                end_line = lines[length - 1]
                result['count_time'] += self.comparetime(first_line[0:18], end_line[0:18])
            except Exception as e:
                print("#####file wrong" + path + "#####")
            # print("count_time", count_time)
            for x in range(length):
                # line = f.readline()
                # for line in f:
                line = lines[x]

                if line.find("am_resume_activity") != -1:  # resume的数据
                    # if line.find("am_on_resume_called") != -1:  # resume的数据
                    # 06-09 21:46:53.637
                    # self.resume_parser(line, temp_resume)
                    ResumeParser().parse(line, result.get('resume'), x, lines, result.get('resume2'),
                                         result.get('resume3'))

                    pass
                # elif line.find("am_crash") != -1:
                #     # match_crash:  # crash 的信息
                #     # self.crashParser(line, temp_crash)
                #     CrashParser().parse(line, result.get("crash"))
                #     # pass
                # elif line.find("am_anr") != -1:
                #     # match_anr:  # anr的数据
                #     # self.anr_parser(line, temp_anr)
                #     AnrParser().parse(line, result.get('anr'))
                elif line.find("screen_toggled") != -1:
                    ScreenParser().parse(length, line, lines, result.get("screen"), result.get("screen_focused"), x,
                                         result.get("resume4"))
                    pass
                elif line.find("proc_start") != -1:
                    # self.proc_parser(length, line, lines, temp_proc, x)
                    ProcParser().parse(length, line, lines, result.get("proc"), x, result.get("proc_start"))
                    # pass
                # elif line.find("am_pss") != -1:
                #     # print("am_pss")
                #     PssParser().parse(line, result.get("pss"))
                #     # pass
                # elif line.find("am_kill") != -1:
                #     KillParser().parse(line, result.get('kill'))
                #
                elif line.find("am_meminfo") != -1:
                    MemParser().parse(line, result.get('mem'))

                elif line.find("battery_level") != -1:
                    BatteryParser().parse(line, result.get("battery"))

                elif line.find("am_activity_launch_time") != -1:
                    LauncherParser().parse(line, result.get("launch"))

                elif line.find("am_on_resume_called") != -1:
                    ResumeCalledParser().parse(line, result.get("resume_called"))
                else:
                    pass
                    # continue
                    # if not line:
                    #     break

    # 画图相关
    def make_sheets(self, results, prefix_name):

        time1 = results.get("count_time")
        print("统计时间总和 = " + str(time1 / HOUR) + " 小时")

        threads = []
        # for k, v in results.iteritems():
        # print k, v
        # v = sorted(v.items(), key=lambda d: d[1][0], reverse=True)
        # print v
        # self.__make_sheet(wb, v, k, fmt)

        # resume 的数据
        v = results.get("resume")
        v = sorted(v.items(), key=lambda d: d[1][0], reverse=True)
        # print(v)
        t = ParseThread(self.make_resume_sheets, (v, "resume", REPORT_PATH + prefix_name + RESUME_REPORT),
                        "resume")
        threads.append(t)
        #
        # # 进程启动
        # v = results.get("proc")
        # t = ParseThread(self.make_proc_sheets, (results, REPORT_PATH + prefix_name + PROC_REPORT), "proc")
        # threads.append(t)
        #
        # # 异常数据 anr crash
        # t = ParseThread(self.make_except_sheets, (results, REPORT_PATH + prefix_name + EXCEPT_REPORT), "except")
        # threads.append(t)
        #
        # # 亮屏解锁的数据
        # v = results.get("screen")
        # t = ParseThread(self.make_screen_sheets, (results, REPORT_PATH + prefix_name + SCREEN_REPORT), "screen")
        # threads.append(t)
        #
        # # 内存变化数据
        # v = results.get("pss")
        # t = ParseThread(self.make_pss_sheets, (v, REPORT_PATH + prefix_name + PSS_REPORT), "pss")
        # threads.append(t)
        #
        # # 杀进程的数据
        # v = results.get("kill")
        # t = ParseThread(self.make_kill_sheets, (v, REPORT_PATH + prefix_name + KILL_REPORT), "kill")
        # threads.append(t)
        #
        # #  内存的数据
        # v = results.get("mem")
        # t = ParseThread(self.make_mem_sheets, (v, REPORT_PATH + prefix_name + MEM_REPORT), "mem")
        # threads.append(t)

        # 电池的数据
        # v = results.get("battery")
        # print(v)
        # t = ParseThread(self.make_battery_sheets, (v, REPORT_PATH + prefix_name + BATTERY_REPORT), "battery")
        # threads.append(t)
        self.threads_run(threads)

        # 进程启动时间和内存状态
        # self.make_launch_sheets(results)

        # app resume time 的时间序列包括灭屏的
        # print(results.get("resume_called"))
        # print(DataFrame(results.get("resume_called")))
        app_results = DataFrame(results.get("resume3")).append(DataFrame(results.get("resume4")))
        app_results = app_results[app_results['pkg'] != "com.tencent.tmgp.sgame"]
        app_results = app_results.append(DataFrame(results.get("resume_called")))

        # 应用的使用时长
        self.make_app_use_time_sheet(app_results)
        # 应用的切换
        self.make_next_app_sheet(app_results)

    def make_next_app_sheet(self, results):
        # 应用的跳转关系
        # 移动一次计算
        data = results.set_index("time").sort_index()
        # data = DataFrame(results.get("resume3")).set_index("time").sort_index()
        # 微信直接跳转过去的应用
        data['next_pkg'] = data['pkg'].shift(-1)
        # 直接跳转到微信，再移动1次 计算
        data['third_pkg'] = data['pkg'].shift(-2)

        # 计算下一个应用 pkg
        # 第2次跳转是桌面com.bbk.launcher2 或者近期任务栏 com.vivo.upslide.recents.RecentsActivity

        # l = ['com.bbk.launcher2', 'com.vivo.upslide.recents.RecentsActivity']
        writer_to = pd.ExcelWriter("csv_record/to.xlsx")
        uniquepkg = data['pkg'].unique()
        # for p in uniquepkg:
        #     # to_data1 = pd.value_counts(data[(data['pkg'] == p) & (~data['next_pkg'].isin(l))]['next_pkg'])
        #     # to_data2 = pd.value_counts(data[(data['pkg'] == p) & (data['next_pkg'].isin(l))]['third_pkg'])
        #     data_all = DataFrame(to_data1).join(DataFrame(to_data2), how="outer").fillna(0)
        #     data_all['all'] = data_all['next_pkg']+data_all['third_pkg']
        #     data_all = data_all.sort_values("all", ascending=False)
        #     # print(data_all)
        #     data_all.to_excel(writer_to, sheet_name=str(p))
        for p in uniquepkg:
            to_data1 = pd.value_counts(data[data['pkg'] == p]['next_pkg'], ascending=False)
            # print(DataFrame(to_data1))
            to_data1.to_excel(writer_to, sheet_name=str(p))

        writer_from = pd.ExcelWriter("csv_record/from.xlsx")
        for p in uniquepkg:
            from_data1 = pd.value_counts(data[data['next_pkg'] == p]['pkg'], ascending=False)
            from_data1.to_excel(writer_from, sheet_name=str(p) if len(str(p)) < 32 else str(p)[:32])
            # pass

    # 应用的使用时长
    def make_app_use_time_sheet(self, results):
        # com.tencent.tmgp.sgame
        # 应用的时长关系
        # results.to_csv("csv_record/results.csv")

        df_all = results.sort_values("time")  # .sort_index()
        df_all.to_csv("csv_record/all.csv")
        # df_all = pd.merge(df_resume3, df_resume4, how="outer", on="time")
        df_all['next_time'] = df_all["time"].shift(-1)
        f1 = "%m-%d %H:%M:%S.%f"
        df_all['timex'] = pd.to_datetime(df_all['next_time'], format=f1) - pd.to_datetime(df_all['time'], format=f1)
        unique_pkg = df_all['pkg']
        d = {}
        for p in unique_pkg:
            wx1 = df_all[df_all['pkg'] == p]
            d[p] = wx1.timex.sum()
        # print(d.values(), d.keys())
        df_final = DataFrame(data=list(d.values()), columns=["time"], index=list(d.keys())).sort_values(by=['time'],
                                                                                                        ascending=False)
        df_final['seconds'] = [x.total_seconds() for x in df_final.time]
        df_final['minutes'] = df_final['seconds'] / 60.0
        w = pd.ExcelWriter("csv_record/fgtime.xlsx")
        df_final.to_excel(w)

    # 启动时间和内存关系
    def make_launch_sheets(self, results):
        df_launch = DataFrame(results.get("launch")).set_index("time").sort_index()
        # df_launch.to_csv("csv_record/launch.csv")
        # print(df_launch.dtypes)
        # 删除>6000ms
        df_launch = df_launch[df_launch['start'] < 6000]

        df_mem = DataFrame(results.get("mem")).set_index("time").sort_index()
        df_mem["free_cached"] = (df_mem["free"].astype(np.float64) + df_mem["cached"].astype(np.float64)) / MB

        # df_resume2 = DataFrame(results.get("resume2")).set_index("time").sort_index()
        # df_resume2.to_csv("csv_record/resume.csv")
        # df_resume2 = df_resume2[df_resume2['interval'] < 6000]

        # print(df_resume2)
        # print(df_launch)
        # print(df_mem)

        # x1 = [parse(item) for item in df_resume2.index]
        x2 = [parse(item) for item in df_mem.index]
        x3 = [parse(item) for item in df_launch.index]

        x_time = pd.date_range(datetime.datetime.date(x2[0]), periods=24 * 4 + 1, freq='H')
        plt.xticks(x_time, [x for x in range(24 * 4 + 1)])

        plt.plot(x2, df_mem["free_cached"], "b-", label="mem")
        # plt.plot(x1, df_resume2["interval"], "r-", label="resume_time")
        plt.plot(x3, df_launch["start"], "y-", label="launch_time")

        plt.xlabel("time")
        plt.ylabel("MB/ms ")

        plt.legend(loc="best")
        plt.show()
        # plt.save("launch.png")
        # pass

    def __make_battery_sheets(self, battery, xlsx_name):
        print("__make_battery_sheets")
        df = DataFrame(battery)
        df2 = df.set_index(['time'])
        df2.to_csv("csv_record/battery.csv")
        # fig = plt.figure()
        # ax0 = fig.add_subplot(131)
        # 　时间字符串转化为时间戳
        time_line = [parse(item) for item in df2.index]
        x_time = pd.date_range(datetime.datetime.date(time_line[0]), periods=24, freq='H')

        plt.plot(time_line, df2['level'].astype(np.int32), 'r--', label="level")
        plt.plot(time_line, [item / 10.0 for item in df2['T'].astype(np.int32)], 'b', label="temperature")
        plt.xticks(x_time, [x for x in range(24)])
        plt.xlabel('time')
        # plt.legend([p1, p2], ['level,temperature'])
        plt.legend(loc="best")
        plt.show()
        # pass

    def make_mem_sheets(self, mem_result, xlsx_name):
        time0 = mem_result.get("time")
        cached = mem_result.get("cached")
        free = mem_result.get("free")
        count = []
        for x1, x2, x3 in zip(time0, cached, free):
            k = x1
            v = (float(x2) + float(x3)) / MB
            count.append((k, v))
        # print(sorted(count))
        count.sort()
        wb = xlsxwriter.Workbook(xlsx_name)
        date_format = wb.add_format({'num_format': 'hh:mm'})
        sheet_name = "FreeMem_spread"
        sheet = wb.add_worksheet(sheet_name)
        chart = wb.add_chart({'type': 'scatter'})
        # sheet.write(0, 0, "time")
        # sheet.write(1, 0, "Free_Mem")
        length = len(count)
        for x in range(length):
            # print(count[x][0][0:5])
            temp = datetime.datetime.strptime(count[x][0][0:5], '%H:%M')
            # print(temp)
            sheet.write_datetime(0, x, temp, date_format)
            sheet.write(1, x, count[x][1])

        chart.add_series({
            'categories': [sheet_name, 0, 0, 0, length],
            'values': [sheet_name, 1, 0, 1, length],
            'marker': {
                'type': 'circle',
                # 'fill': {'color': 'red'},
            },
        })

        chart.set_title({
            'name': "mem_spread_results",
            'name_font': {
                'color': 'blue',
            },
        })

        chart.set_x_axis({
            'date_axis': True,
            # 'time_axis': True,
            'min': datetime.time(0),
            'max': datetime.time(23, 59),
            'name': "Time",
            'name_font': {
                'name': 'Courier New',
                'color': '#92D050'
            },
            'num_font': {
                'name': 'Arial',
                'color': '#00B0F0',
            },

            # 'minor_unit': 60,
            # 'minor_unit_type': 'minutes',
            # 'major_unit': 24,
            # 'major_unit_type': 'hours',
            # 'num_format': 'dd/mm/yy hh:mm:ss',
            # 'interval_unit': 24,
            'num_format': 'hh:mm',
            'major_gridlines': {
                'visible': True,
                'line': {'width': 1.25, 'dash_type': 'dash'}
            },
        })

        chart.set_y_axis({
            'name': "FreeMem",
            'name_font': {
                'name': 'Century',
                'color': 'red'
            },
            'num_font': {
                'bold': True,
                'italic': True,
                'underline': True,
                'color': '#7030A0',
            },
        })
        chart.set_size({  # 设置图表整体的大小
            'width': 1200,  # 宽
            'height': 600,  # 高
        })
        # print(count)
        sheet.insert_chart(4, 0, chart)
        wb.close()
        # pass

    def make_kill_sheets(self, kill_result, xlsx_name):
        # print(kill_result)
        sort_list = sorted(kill_result.items(), key=lambda d: d[1], reverse=True)
        wb = xlsxwriter.Workbook(xlsx_name)
        sheet = wb.add_worksheet("kill")
        sheet.write(0, 0, "PROC_NAME")
        sheet.write(0, 1, "TIMES")
        for i in range(len(sort_list)):
            sheet.write(i + 1, 0, sort_list[i][0])
            sheet.write(i + 1, 1, sort_list[i][1])
        wb.close()
        # pass

    def make_pss_sheets(self, pss_list, xlsx_name):
        pss = sorted(pss_list.items(), key=lambda d: d[0])
        # print(pss)
        wb = xlsxwriter.Workbook(xlsx_name)
        # pss_mb = [i/MB for i in pss[1][0]]
        # i = 0
        # for v in pss:
        #     sheet.write(i, 0, v[0])
        #     pss_mb = [float(i)/MB for i in v[1][0]]
        #     avg = np.mean(pss_mb)
        #     # for j in range(len(pss_mb)):
        #     sheet.write(i, 1, avg)
        #     i += 1
        list_arr = [50, 100, 200, 300, 400, 500, 1000]
        spread_dict = self.method_spread2(list_arr, pss)
        self.make_proc_spread_sheet(wb, "pss_spread_sheet", spread_dict, self.generate_unit(list_arr))
        wb.close()
        # pass

    def method_spread2(self, list_arr, sort_list):
        # print(sort_list)
        len1 = len(list_arr)
        spread_dict = {}
        for v in sort_list:
            process = v[0]
            # print(v)
            interval = [(float(i) / MB) for i in v[1][0]]
            arr = [i for i in np.array(interval)]
            avg = 0 if len(arr) == 0 else np.mean(arr)
            # avg = np.mean(arr)
            values = [0] * (len1 + 1)
            for i in interval:
                for j in range(len1):
                    if i < list_arr[j]:
                        values[j] += 1
                        break
                    if j == len1 - 1:
                        values[len1] += 1
            spread_dict[process] = [values, avg]
        return spread_dict

    def make_screen_sheets(self, results, xlsx_name):
        print("__make_screen_sheets")
        wb = xlsxwriter.Workbook(xlsx_name)
        v = results.get("screen")
        self.make_screen_onoff_sheet(wb, v, "screen_onoff")
        v = results.get("screen_focused")
        self.make_screen_focused_sheet(wb, v, "screen_focused")
        wb.close()

    def make_screen_onoff_sheet(self, wb, sort_list, sheet_name):
        print("__make_screen_onoff_sheet")
        screen_map = {'0': '灭屏', '1': "亮屏", '2': "指纹解锁"}
        sheet = wb.add_worksheet(sheet_name)
        i = 0
        for k, v in sort_list.items():
            title = screen_map.get(k, k)
            sheet.write(i, 0, title)
            sheet.write(i, 1, v[0])
            i += 1

    def make_screen_focused_sheet(self, wb, sort_list, sheet_name):
        print("__make_screen_focused_sheet")
        sheet = wb.add_worksheet(sheet_name)
        count = sort_list.pop("count")
        sheet.write(0, 0, "PkgName")
        sheet.write(0, 0, "Times")
        value = sorted(sort_list.items(), key=lambda d: d[1], reverse=True)
        i = 1
        for k in value:
            sheet.write(i, 0, k[0])
            sheet.write(i, 1, k[1])
            i += 1

    # 进程信息的表
    def make_proc_sheets(self, results, xlsx_name):
        print("__make_proc_sheets")
        sort_dict = results.get("proc")
        sort_start = results.get("proc_start")
        wb = xlsxwriter.Workbook(xlsx_name)

        sheet = wb.add_worksheet("proc_start")
        sort1 = sorted(sort_start.items(), key=lambda d: d[1], reverse=True)
        for i in range(len(sort1)):
            sheet.write(i, 0, sort1[i][0])
            sheet.write(i, 1, sort1[i][1])

        # fmt = wb.add_format()
        sort_list = sorted(sort_dict.items(), key=lambda d: d[0], reverse=False)
        # print("proc_list", sort_list)

        list_arr = [50, 100, 1000]
        spread_dict = self.method_spread(list_arr, sort_list)
        # print(spread_dict)
        self.make_proc_spread_sheet(wb, "spread_sheet", spread_dict, self.generate_unit(list_arr))
        # self.__make_proc_main_sheet(wb, sort_list, fmt)
        # for k in sort_list:
        #     key = k[0].replace
        #     self.__make_proc_sub_sheet(wb, k[0], k[1][0])
        wb.close()

    #
    def method_spread(self, list_arr, sort_list):
        len1 = len(list_arr)
        spread_dict = {}
        for v in sort_list:
            process = v[0]
            interval = v[1][0]
            # arr = [float(i) for i in np.array(interval) if i < 100]
            arr = [float(i) for i in np.array(interval)]
            avg = 0 if len(arr) == 0 else np.mean(arr)
            # avg = np.mean(arr)
            values = [0] * (len1 + 1)
            for i in interval:
                for j in range(len1):
                    if i < list_arr[j]:
                        values[j] += 1
                        break
                    if j == len1 - 1:
                        values[len1] += 1
            spread_dict[process] = [values, avg]
        return spread_dict

    # 生成区间段的list
    def generate_unit(self, list_arr):
        list_arr.sort()
        keys = []
        size = len(list_arr)
        i = 0
        while i < size:
            if i == 0:
                key = '<' + str(list_arr[i])
            else:
                key = str(list_arr[i - 1]) + '-' + str(list_arr[i])
            keys.append(key)
            i += 1
        keys.append('>' + str(list_arr[-1]))
        return keys

    def make_proc_spread_sheet(self, wb, sheet_name, sort_list, keys):
        sheet = wb.add_worksheet(sheet_name)
        # print(keys)
        len1 = len(keys)
        sheet.write(0, 0, "PROC_NAME")
        sheet.write(0, len1 + 1, "AVEG(M/ms)")
        for x in range(0, len1):
            sheet.write(0, x + 1, keys[x])
        sorted_list = sorted(sort_list.items(), key=lambda d: d[0])
        i = 1
        for v in sorted_list:
            sheet.write(i, 0, v[0])
            sheet.write(i, len1 + 1, v[1][1])
            l = v[1][0]
            len2 = len(l)
            for x in range(len2):
                sheet.write(i, x + 1, l[x])
            i += 1

    def make_proc_sub_sheet(self, wb, sheet_sub_name, sort_list):
        sheet = wb.add_worksheet(sheet_sub_name)
        i = 1
        for k in sort_list:
            sheet.write(i, 0, i)
            sheet.write(i, 1, k)
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style(chart, i, sheet_sub_name, "Activity", "Times")

    def make_proc_main_sheet(self, wb, sort_list, fmt):
        print("__make_proc_main_sheet")
        sheet = wb.add_worksheet("proc_main")
        i = 0
        for k in sort_list:
            # key = k[0].replace(":", ".")
            key = k[0]
            link = 'internal:%s!%s' % (key, utility.xl_rowcol_to_cell(0, 0))
            sheet.write(i, 0, link, fmt, key)
            for x in range(len(k[1][0])):
                sheet.write(i, x + 1, k[1][0][x])
            # self.__make_proc_sub_sheet(wb, key, k[1][0])
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style3(chart, sort_list, "proc_main", "times", "Time(/ms)")

    def gen_chart_style3(self, chart, sort_list, sheet_name, x_name, y_name):
        i = len(sort_list)
        # l = list(d.keys())
        # print("gen_chart_style3", sort_list)
        for x in range(0, i):
            chart.add_series({
                # 'categories': [sheet_name, 0, 0, 25, 0],
                'values': [sheet_name, x, 0, x, len(sort_list[x][0])],
                'name': sort_list[x][0],
                'marker': {'type': 'diamond'},
            })

        chart.set_title({
            'name': sheet_name + "_results",
            'name_font': {
                'color': 'blue',
            },
        })
        chart.set_x_axis({
            'name': x_name,
            'name_font': {
                'name': 'Courier New',
                'color': '#92D050'
            },
            'num_font': {
                'name': 'Arial',
                'color': '#00B0F0',
            },
        })
        chart.set_y_axis({
            'name': y_name,
            'name_font': {
                'name': 'Century',
                'color': 'red'
            },
            'num_font': {
                'bold': True,
                'italic': True,
                'underline': True,
                'color': '#7030A0',
            },
        })
        chart.set_size({  # 设置图表整体的大小
            'width': 1200,  # 宽
            'height': 600,  # 高
        })

    # 异常数据的图表
    def make_except_sheets(self, results, xlsx_name):
        # print("__make_exception_sheets")
        wb = xlsxwriter.Workbook(xlsx_name)
        # crash 的数据
        v = results.get("crash")
        v = sorted(v.items(), key=lambda d: d[1], reverse=True)
        self.make_except_sheet(v, wb, "crash")

        # anr 的数据
        v = results.get("anr")
        v = sorted(v.items(), key=lambda d: d[1], reverse=True)
        self.make_except_sheet(v, wb, "anr")
        wb.close()

    # 异常数据的子表
    def make_except_sheet(self, sort_list, wb, sheet_name):
        print("__make_exception_sheet")
        sheet = wb.add_worksheet(sheet_name)
        sheet.write(0, 0, "PkgName")
        sheet.write(0, 1, "Times")
        i = 1
        for k in sort_list:
            sheet.write(i, 0, k[0])
            sheet.write(i, 1, k[1][0])
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style(chart, i, sheet_name, "PkgName", "Times")

    # resume activity 的数据
    def make_resume_sheets(self, sorted_tuple, sheet_name, xlsx_name):
        wb = xlsxwriter.Workbook(xlsx_name)
        fmt = wb.add_format()
        self.make_main_sheet(sheet_name, sorted_tuple, wb, fmt)
        self.make_app_spread_sheet(wb, sorted_tuple, "app_resume_time_spread", fmt)
        for k in sorted_tuple:
            self.make_resume_sub_sheet(wb, k[0], k[1][1])
        wb.close()

    # resume activity 的时间分布
    def make_app_spread_sheet(self, wb, sorted_tuple, sheet_name, fmt):
        # d1 = {"00":0,"01":1}
        print("__make_app_spread_sheet")
        sheet = wb.add_worksheet(sheet_name)
        sheet.write(0, 0, "Time")
        # sheet.write(0, 1, "PkgName")
        # sheet.write(0, 1, "Times")
        for x in range(0, 24):
            sheet.write(x + 1, 0, str(x) + u"点")
        tmp_dict = {}
        for k in sorted_tuple:
            res = k[1][2]
            tmp = []
            for k0 in res:
                # 11-02 16:11:57.160
                tmp.append(k0[6:8])
            tmp_dict[k[0]] = dict(Counter(tmp))
        # print("tmp_dict", tmp_dict)

        i = 1
        for k, v in tmp_dict.items():
            # print "====", k, v
            sheet.write(0, i, k)
            for x in range(1, 25):
                sheet.write(x, i, 0)
            for k1, v1 in v.items():
                sheet.write(int(k1) + 1, i, v1)
            i += 1
        # chart = wb.add_chart({'type': 'scatter'})
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(25 + 1, 0, chart)
        self.gen_chart_style2(chart, tmp_dict, sheet_name, "Time", "Times")

    def make_main_sheet(self, sheet_name, sorted_tuple, wb, fmt):
        sheet = wb.add_worksheet(sheet_name)
        sheet.write(0, 0, "PkgName")
        sheet.write(0, 1, "Times")
        i = 1
        for k in sorted_tuple:
            sheet.write(i, 0, k[0])
            sheet.write(i, 1, k[1][0])
            link = 'internal:%s!%s' % (k[0], utility.xl_rowcol_to_cell(0, 0))
            sheet.write(i, 2, link, fmt, u"点击详细")
            # wb, activity_sorted, sheet_sub_name
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style(chart, i, sheet_name, "Packages", "Times")

    # // link = 'internal:%s!%s' % (u"anr_trace"+str(i-1), utility.xl_rowcol_to_cell(0, i-1))
    def make_resume_sub_sheet(self, wb, sheet_sub_name, activity_dict):
        # print 'make_sub_sheet'
        activity_sorted = sorted(activity_dict.items(), key=lambda d: d[1], reverse=True)
        # print activity_sorted
        sheet = wb.add_worksheet(sheet_sub_name)
        sheet.write(0, 0, "Activity")
        sheet.write(0, 1, "Times")
        i = 1
        for k in activity_sorted:
            sheet.write(i, 0, k[0])
            sheet.write(i, 1, k[1])
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style(chart, i, sheet_sub_name, "Activity", "Times")

    def gen_chart_style(self, chart, i, sheet_name, x_name, y_name):
        chart.add_series({
            'categories': [sheet_name, 1, 0, i, 0],
            'values': [sheet_name, 1, 1, i, 1],
            'line': {'color': 'red'},
            'marker': {'type': 'diamond'},
        })
        chart.set_title({
            'name': sheet_name + "_results",
            'name_font': {
                'color': 'blue',
            },
        })
        chart.set_x_axis({
            'name': x_name,
            'name_font': {
                'name': 'Courier New',
                'color': '#92D050'
            },
            'num_font': {
                'name': 'Arial',
                'color': '#00B0F0',
            },
        })
        chart.set_y_axis({
            'name': y_name,
            'name_font': {
                'name': 'Century',
                'color': 'red'
            },
            'num_font': {
                'bold': True,
                'italic': True,
                'underline': True,
                'color': '#7030A0',
            },
        })
        chart.set_size({  # 设置图表整体的大小
            'width': 1000,  # 宽
            'height': 500,  # 高
        })

    def gen_chart_style2(self, chart, d, sheet_name, x_name, y_name):
        i = len(d)
        l = list(d.keys())
        # print("gen_chart_style2", l)
        for x in range(1, i + 1):
            chart.add_series({
                'categories': [sheet_name, 1, 0, 25, 0],
                'values': [sheet_name, 1, x, 25, x],
                'name': l[x - 1],
                'marker': {'type': 'diamond'},
            })

        chart.set_title({
            'name': sheet_name + "_results",
            'name_font': {
                'color': 'blue',
            },
        })
        chart.set_x_axis({
            'name': x_name,
            'name_font': {
                'name': 'Courier New',
                'color': '#92D050'
            },
            'num_font': {
                'name': 'Arial',
                'color': '#00B0F0',
            },
        })
        chart.set_y_axis({
            'name': y_name,
            'name_font': {
                'name': 'Century',
                'color': 'red'
            },
            'num_font': {
                'bold': True,
                'italic': True,
                'underline': True,
                'color': '#7030A0',
            },
        })
        chart.set_size({  # 设置图表整体的大小
            'width': 1200,  # 宽
            'height': 600,  # 高
        })

    def threads_run(self, threads):
        for t in threads:
            t.start()
        for t in threads:
            t.join()


if __name__ == '__main__':
    start = time.time()
    print("parse start at ...")
    # eventlog = EventLog(DIR, "PD1610")
    # eventlog = EventLog(DIR3, "PD1619")
    eventlog = EventLog(DIR2, "test")
    eventlog.parse()
    # EventLog("D:/log/eventlog/PD1619/", "PD1619").parse()
    end = time.time() - start
    print("parse and make sheet end in %.1f s" % end)
# thread = ParseThread("Thread-1", 1)
# thread.start()
