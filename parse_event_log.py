#!/usr/bin/env python
# coding:utf-8

__author = 'zhaoxiaowen'
import threading
import time
from collections import Counter

import xlsxwriter
import xlsxwriter.utility as utility

from event_parser.parsers import *

DIR = "E:/Project/Pycharm/ftp_work/event/events_log"
REPORT_PATH = "E:/Project/Pycharm/ftp_work/event_report/"

RESUME_PATTERN = r"(.*)\s+\d+\s+\d+ I am_resume_activity: \[(\d+,){3}(.*)/(.*)\]"
FOCUSED_PATTERN = r".* am_focused_activity: \[\d+,(.*)/.*\]"
CRASH_PATTERN = r"(.*)\s+\d+\s+\d+ I am_crash: \[(\d+,){2}(.*),\d+,.*\]"
ANR_PATTERN = "(.*)\s+\d+\s+\d+ I am_anr: \[(\d+,){2}(.*),\d+,.*\]"
SCREEN_PATTERN = "(.*)\s+\d+\s+\d+ I screen_toggled: (\d+)"

START_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_start: \[(\d+,){3}(.*),(.*),.*\]"
BOUND_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_bound: \[(\d+,){2}(.*)\]"


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
    def __init__(self, path):
        # print("init")
        self.path = path

    def parse(self, rev=True):
        start_time = time.time()
        results = self.parse_files()
        end_time = time.time() - start_time
        print("parse files end %.1f s" % end_time)
        # print(results)
        # print results.get("screen").keys()
        # for k, v in results.get("screen").items():
        #     print(k, v)
        self.make_sheets(results)

    def comparetime(self, time1, time2):
        return (parse(time2) - parse(time1)).total_seconds() * 1000

    def parse_files(self):
        # result = {'resume': {}, 'focused': {}}
        result = {'resume': {}, 'crash': {}, 'anr': {}, 'screen': {}, "proc": {}, "screen_focused": {"count": 1}}
        temp_resume = result.get('resume')
        temp_crash = result.get("crash")
        temp_anr = result.get('anr')
        temp_proc = result.get("proc")
        temp_screen = result.get("screen")
        temp_screen_focused = result.get("screen_focused")
        # 多个路径 这里加循环 for path in paths:
        with open(self.path, encoding="utf-8") as f:
            # while True:
            lines = f.readlines()
            length = len(lines)
            for x in range(length):
                # line = f.readline()
                # for line in f:
                line = lines[x]
                # match_resume = re.search(RESUME_PATTERN, line)
                # match_crash = re.search(CRASH_PATTERN, line)
                # match_anr = re.search(ANR_PATTERN, line)
                # match_screen = re.search(SCREEN_PATTERN, line)
                # match_start = re.search(START_PATTERN, line)

                if line.find("am_resume_activity") != -1:  # resume的数据
                    # 06-09 21:46:53.637
                    # self.resume_parser(line, temp_resume)
                    ResumeParser().parse(line, temp_resume)
                    # pass
                elif line.find("am_crash") != -1:
                    # match_crash:  # crash 的信息
                    # self.crashParser(line, temp_crash)
                    CrashParser().parse(line, temp_crash)
                    # pass
                elif line.find("am_anr") != -1:
                    # pass
                    # match_anr:  # anr的数据
                    # self.anr_parser(line, temp_anr)
                    AnrParser().parse(line, temp_anr)
                    # pass
                elif line.find("screen_toggled") != -1:
                    # self.screen_parser()
                    ScreenParser().parse(length, line, lines, temp_screen, temp_screen_focused, x)
                    # pass
                elif line.find("proc_start") != -1:
                    # self.proc_parser(length, line, lines, temp_proc, x)
                    ProcParser().parse(length, line, lines, temp_proc, x)
                    # pass
                else:
                    pass
                    # continue
                    # if not line:
                    #     break
        # result[] = temp

        return result

    #   画图相关
    def make_sheets(self, results):
        threads = []
        # for k, v in results.iteritems():
        # print k, v
        # v = sorted(v.items(), key=lambda d: d[1][0], reverse=True)
        # print v
        # self.__make_sheet(wb, v, k, fmt)

        # resume 的数据
        v = results.get("resume")
        v = sorted(v.items(), key=lambda d: d[1][0], reverse=True)
        # print v
        t = ParseThread(self.__make_resume_sheets, (v, "resume", REPORT_PATH + "event_log_resume_results.xlsx"),
                        "resume")
        threads.append(t)

        # 进程启动
        v = results.get("proc")
        t = ParseThread(self.__make_proc_sheets, (v, REPORT_PATH + "event_log_proc_results.xlsx"), "proc")
        threads.append(t)

        # 异常数据 anr crash
        t = ParseThread(self.__make_except_sheets, (results, REPORT_PATH + "event_log_except_results.xlsx"), "except")
        threads.append(t)

        # 亮屏解锁的数据
        v = results.get("screen")
        t = ParseThread(self.__make_screen_sheets, (results, REPORT_PATH + "/event_log_screen_results.xlsx"), "screen")

        threads.append(t)

        self.threads_run(threads)

        # self.__make_resume_sheets(v, "resume")
        #

    def __make_screen_sheets(self, results, xlsx_name):
        print("__make_screen_sheets")
        wb = xlsxwriter.Workbook(xlsx_name)
        v = results.get("screen")
        self.__make_screen_onoff_sheet(wb, v, "screen_onoff")
        v = results.get("screen_focused")
        self.__make_screen_focused_sheet(wb, v, "screen_focused")
        wb.close()

    def __make_screen_onoff_sheet(self, wb, sort_list, sheet_name):
        print("__make_screen_onoff_sheet")
        screen_map = {'0': '灭屏', '1': "亮屏", '2': "指纹解锁"}
        sheet = wb.add_worksheet(sheet_name)
        i = 0
        for k, v in sort_list.items():
            title = screen_map.get(k, k)
            sheet.write(i, 0, title)
            sheet.write(i, 1, v[0])
            i += 1

    def __make_screen_focused_sheet(self, wb, sort_list, sheet_name):
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
    def __make_proc_sheets(self, sort_dict, xlsx_name):
        print("__make_proc_sheets")
        wb = xlsxwriter.Workbook(xlsx_name)
        fmt = wb.add_format()
        sort_list = sorted(sort_dict.items(), key=lambda d: d[0], reverse=False)
        # print("sort_list", sort_list)
        self.__make_proc_main_sheet(wb, sort_list, fmt)
        # for k in sort_list:
        #     key = k[0].replace
        #     self.__make_proc_sub_sheet(wb, k[0], k[1][0])
        wb.close()

    def __make_proc_sub_sheet(self, wb, sheet_sub_name, sort_list):
        sheet = wb.add_worksheet(sheet_sub_name)
        i = 1
        for k in sort_list:
            sheet.write(i, 0, i)
            sheet.write(i, 1, k)
            i += 1
        chart = wb.add_chart({'type': 'line'})
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style(chart, i, sheet_sub_name, "Activity", "Times")

    def __make_proc_main_sheet(self, wb, sort_list, fmt):
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
    def __make_except_sheets(self, results, xlsx_name):
        # print("__make_exception_sheets")
        wb = xlsxwriter.Workbook(xlsx_name)
        # crash 的数据
        v = results.get("crash")
        v = sorted(v.items(), key=lambda d: d[0], reverse=True)
        self.__make_except_sheet(v, wb, "crash")

        # anr 的数据
        v = results.get("anr")
        v = sorted(v.items(), key=lambda d: d[0], reverse=True)
        self.__make_except_sheet(v, wb, "anr")
        wb.close()

    # 异常数据的子表
    def __make_except_sheet(self, sort_list, wb, sheet_name):
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
    def __make_resume_sheets(self, sorted_tuple, sheet_name, xlsx_name):
        wb = xlsxwriter.Workbook(xlsx_name)
        fmt = wb.add_format()
        self.__make_main_sheet(sheet_name, sorted_tuple, wb, fmt)
        self.__make_app_spread_sheet(wb, sorted_tuple, "app_resume_time_spread", fmt)
        for k in sorted_tuple:
            self.make_resume_sub_sheet(wb, k[0], k[1][1])
        wb.close()

    # resume activity 的时间分布
    def __make_app_spread_sheet(self, wb, sorted_tuple, sheet_name, fmt):
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
                tmp.append(k0[0:2])
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
        sheet.insert_chart(i + 1, 0, chart)
        self.gen_chart_style2(chart, tmp_dict, sheet_name, "Time", "Times")

    def __make_main_sheet(self, sheet_name, sorted_tuple, wb, fmt):
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
    eventlog = EventLog(DIR)
    eventlog.parse()
    end = time.time() - start
    print("parse and make sheet end in %.1f s" % end)
# thread = ParseThread("Thread-1", 1)
# thread.start()
