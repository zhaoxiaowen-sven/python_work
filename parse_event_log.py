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
import os
import threading
import time

from pandas import DataFrame

from event_parser.parsers import *
from sheet_builder import SheetBuilder

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
        builder = SheetBuilder()
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
        t = ParseThread(builder.make_resume_sheets, (v, "resume", REPORT_PATH + prefix_name + RESUME_REPORT),
                        "resume")
        threads.append(t)
        #
        # # 进程启动
        # v = results.get("proc")
        # t = ParseThread(builder.make_proc_sheets, (results, REPORT_PATH + prefix_name + PROC_REPORT), "proc")
        # threads.append(t)
        #
        # # 异常数据 anr crash
        # t = ParseThread(builder.make_except_sheets, (results, REPORT_PATH + prefix_name + EXCEPT_REPORT), "except")
        # threads.append(t)
        #
        # # 亮屏解锁的数据
        # v = results.get("screen")
        # t = ParseThread(builder.make_screen_sheets, (results, REPORT_PATH + prefix_name + SCREEN_REPORT), "screen")
        # threads.append(t)
        #
        # # 内存变化数据
        # v = results.get("pss")
        # t = ParseThread(builder.make_pss_sheets, (v, REPORT_PATH + prefix_name + PSS_REPORT), "pss")
        # threads.append(t)
        #
        # # 杀进程的数据
        # v = results.get("kill")
        # t = ParseThread(builder.make_kill_sheets, (v, REPORT_PATH + prefix_name + KILL_REPORT), "kill")
        # threads.append(t)
        #
        # #  内存的数据
        # v = results.get("mem")
        # t = ParseThread(builder.make_mem_sheets, (v, REPORT_PATH + prefix_name + MEM_REPORT), "mem")
        # threads.append(t)

        # 电池的数据
        # v = results.get("battery")
        # print(v)
        # t = ParseThread(builder.make_battery_sheets, (v, REPORT_PATH + prefix_name + BATTERY_REPORT), "battery")
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
        builder.make_app_use_time_sheet(app_results)
        # 应用的切换
        builder.make_next_app_sheet(app_results)

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
