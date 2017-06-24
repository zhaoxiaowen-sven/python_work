#!/usr/bin/env python
# coding:utf-8
import os
import re
from collections import Counter
from copy import deepcopy
from os import walk

import xlsxwriter

# from ftpdownload3 import FtpDownload
import ftpdownload
from utils.config_utils import ConfigUtils
from utils.time_utils import TimeUtils

# 读取配置文件
caseMaps, appMaps, deviceMaps = ConfigUtils.readConfig()

# print caseMaps, appMaps, deviceMaps
# print "caseMaps", caseMaps
today = TimeUtils.getTodayTimeStamp()
today = "170610"


# 170610115939

def parse_logs():
    # ftpdown = ftpdownload3.FtpDownload()
    # ftpdown.download("172.25.105.226", "UniversalTest/performance_ScenarioTest/", "20170610115900")
    # 6.7.1//7.0.0
    dir1 = "logs/PD1619/" + today + "/"
    dir2 = "logs/PD1610/" + today + "/"
    # dir2 = "logs/PD1635/" + today + "/"
    # dir2 = "logs/PD1610/" + today + "/"
    # dir3 = "logs/PD1616/" + today + "/"
    parse_log(dir1, "PD1619")
    parse_log(dir2, "PD1610")
    # parse_log(dir2, "PD1610")
    # parse_log(dir3, "PD1616")
    # dir4 = "logs/S8/"
    # dir5 = "logs/PD1635/"
    # dir6 = "logs/Mi6/"
    # make_sheets(dpkgs, dcases, fps_dict, model)
    # parse_log(dir4,"S8")
    # parse_log(dir5,"PD1635")
    # parse_log(dir6, "Mi6")
    # parse_log(dir2, "PD1610")


def parse_log(root, model):
    print("parse_log")
    debug_path = root + "debug/"
    event_path = root + "event/"
    debug_log_files = get_target_filenames(debug_path)
    event_log_files = get_target_filenames(event_path)
    print(debug_log_files, event_log_files)

    anr_dict = parse_event_log(event_log_files, event_path)
    print(anr_dict)
    dcases, dpkgs, fps_dict = parse_debug_file(debug_log_files, debug_path)
    # print dcases,dpkgs
    make_report_sheets(dpkgs, dcases, fps_dict, model, anr_dict)

    # return dpkgs, dcases, fps_dict


# 解析eventlog 文件
def parse_event_log(files, path):
    print("parse_event_log")
    anr_dict = {}
    detail_dict = {}
    for f in files:
        temp_path = path + f
        if os.path.exists(temp_path):
            with open(temp_path) as readfile:
                for line in readfile:
                    if line.find("am_anr") != -1:
                        matchObj = re.search(r"\[\d+,\d+,(.*),\d+,(.*)\]", line)
                        if matchObj:
                            pkgname = matchObj.group(1)
                            reason = matchObj.group(2)
                            # print pkgName,reason
                            if pkgname in anr_dict.keys():
                                value = anr_dict.get(pkgname)
                                value[0] += 1
                                value[1].append(temp_path)
                                anr_dict[pkgname] = value
                            else:
                                anr_dict[pkgname] = [1,[temp_path]]
                            # if reason in detail_dict.keys():
                            #     value = detail_dict.get(reason) + 1
                            #     detail_dict[reason] = value
                            # else:
                            #     detail_dict[reason] = 1
    # print anr_dict
    # anr_dict["details"] = detail_dict
    return anr_dict


# 解析debuglog 文件
def parse_debug_file(files, path):
    print("parse_debug_file")
    pkgs = []
    cases = []
    fps_dict = {}
    for f in files:
        with open(path + f) as readfile:
            for line in readfile:
                if line.find("bugreport") != -1:
                    matchobj = re.search(r"frames.*: (\d+).*u'(\d+)'", line)
                    if matchobj:
                        # print matchobj.group()
                        fps = int(matchobj.group(1))
                        case = matchobj.group(2)
                        pkg = case[0:2]
                        if len(pkg) != 0 or len(case) != 0 or len(fps) != 0:
                            # if pkg.startswith('05') or pkg.startswith('06'):
                            #     continue
                            if case.startswith('0500') or case.startswith('0600'):
                                continue
                            # if pkg != "02":
                            #     continue
                            pkgs.append(pkg)
                            cases.append(case)
                            if fps_dict.get(case, 0) != 0:
                                fps_dict.get(case).append(fps)
                            else:
                                # fps_list = []
                                # fps_list.append(fps)
                                fps_dict[case] = [fps]
                    else:
                        print("No match!!")
                        continue
    # print fps_dict
    # print pkgs
    # print cases
    # print ' lose fps times  = ' + str(len(pkgs))
    dpkgs = dict(Counter(pkgs))
    dcases = dict(Counter(cases))
    return dcases, dpkgs, fps_dict


# 获取目标路径下的所有文件
def get_target_filenames(path):
    for dirpath, dirnames, filenames in walk(path):
        return filenames


# 生成表格
def make_report_sheets(dpkgs, dcases, fps_dict, model, anr_dict):
    # print dpkgs
    # print dcases
    # time_stamp = TimeUtils.getTodayTimeStamp()
    path = "report/" + today + "/"
    if not os.path.exists(path):
        os.makedirs(path)

    sheet_writer = xlsxwriter.Workbook(path + model + "_" + today + "_results.xlsx")
    make_sheet1(dcases, dpkgs, model, sheet_writer)
    l = [30, 40, 50, 60]
    make_fps_sheet(fps_dict, sheet_writer, l)
    make_fps_detail_sheet(fps_dict, sheet_writer, l)
    make_anr_sheet(anr_dict, sheet_writer)
    sheet_writer.close()

def make_anr_sheet(anr_dict, sheet_writer):
    sheet = sheet_writer.add_worksheet(u'应用anr次数统计及路径')
    i = 0
    for k, v in anr_dict.items():
        sheet.write(i, 0, k)
        sheet.write(i, 1, v[0])
        j = 2
        for v0 in v[1]:
            sheet.write(i, j, v0)
            j += 1

def make_fps_detail_sheet(fps_dict, sheet_writer, list):
    print("make_fps_detail_sheet")
    sheet = sheet_writer.add_worksheet("fps_detail")

    fps_dict_copy = deepcopy(fps_dict)
    for k in fps_dict_copy:
        fps_dict_copy.get(k).sort()
    # print fps_dict_copy

    i = 0
    for k1 in fps_dict_copy:
        l = fps_dict_copy.get(k1)
        j = 0
        for k2 in l:
            if j == 0:
                case = caseMaps.get(k1)
                if case is not None:
                    k1 = case
                sheet.write(i, j, k1)
            sheet.write(i, j + 1, k2)
            j += 1
        i += 1

    i = 0
    length1 = len(fps_dict_copy)
    for k1 in fps_dict_copy:
        length2 = len(fps_dict_copy.get(k1))
        exe_fps_chart(sheet_writer, sheet, length1 + 1 + i * 15, "fps_detail", i, 1, i, length2, caseMaps.get(k1))
        i += 1

    dict_section = {}
    # keys =
    keys = generate_unit(list)
    # print keys
    # 统计分区段的元素的个

    dict_values = {}
    for k in fps_dict_copy:
        dlist = fps_dict_copy.get(k)  # 需要计算排序的数组
        dlen = len(dlist)
        i = 0  # 记录外层循环的次数
        count = dlen
        len2 = len(list)
        values = [0] * (len2 + 1)

        for k0 in dlist:
            j = 0
            # if (k0 > list[len2-1]):
            #     values[len2] = dlen - sum(values[0:len2 - 1])
            #     break
            for k1 in list:
                if k0 < k1:
                    values[j] += 1
                    break
                if j == len2 - 1:
                    values[len2] += 1
                j += 1
        dict_values[k] = values
        # print dict_values[k]

    sheet = sheet_writer.add_worksheet("fps_detail_spread")

    # 写坐标轴数据
    i = 0
    for k in keys:
        sheet.write(0, i + 1, k)
        i += 1
    i = 0
    for k1 in dict_values:
        l = dict_values.get(k1)
        j = 0
        for k2 in l:
            if j == 0:
                case = caseMaps.get(k1)
                if case is not None:
                    k1 = case
                sheet.write(i + 1, j, k1)
            sheet.write(i + 1, j + 1, k2)
            j += 1
        i += 1
    i = 1
    for k1 in dict_values:
        length2 = len(dict_values.get(k1))
        exe_fps_chart2(sheet_writer, sheet, length1 + 1 + (i - 1) * 15, "fps_detail_spread", i, 1, i, length2,
                       caseMaps.get(k1), i)
        i += 1


# 生成区间段的list
def generate_unit(list):
    list.sort()
    keys = []
    size = len(list)
    i = 0
    while i < size:
        if i == 0:
            key = '<' + str(list[i])
        else:
            key = str(list[i - 1]) + '-' + str(list[i])
        keys.append(key)
        i += 1
    keys.append('>' + str(list[-1]))
    return keys


def make_fps_sheet(fps_dict, sheet_writer, list):
    print("make_fps_sheet")
    keys = generate_unit(list)
    sheet = sheet_writer.add_worksheet("fps")
    point = 0
    size = len(fps_dict)
    list_all = []
    for k in fps_dict.keys():
        list_all.extend(fps_dict.get(k))

    list_all.sort()
    print(1111)
    for index, value in enumerate(list_all):
        sheet.write(0, index, value)

    len2 = len(list)
    # print "len2:", len2 - 1
    values = [0] * (len2 + 1)
    for k0 in list_all:
        j = 0
        for k1 in list:
            if k0 < k1:
                values[j] += 1
                break
            if j == len2 - 1:
                values[len2] += 1
            j += 1
    print(keys, values)
    i = 0
    for k in keys:
        sheet.write(2, i, k)
        sheet.write(3, i, values[i])
        i += 1
    exe_fps_chart2(sheet_writer, sheet, 4, "fps", 3, 0, 3, len2, u"掉帧数分布", 1)


def make_sheet1(dcases, dpkgs, model, sheet_writer):
    print("make_sheet1")
    print(dcases)
    print (dpkgs)

    sortedcases = sorted(dcases.iteritems(), key=lambda d: d[1], reverse=True)
    sortedpkgs = sorted(dpkgs.iteritems(), key=lambda d: d[1], reverse=True)
    sheet = sheet_writer.add_worksheet(model)
    chart0 = sheet_writer.add_chart({'type': 'column'})
    chart1 = sheet_writer.add_chart({'type': 'column'})
    i = 0
    # for k in dpkgs.keys():
    for k in sortedpkgs:
        if i == 0:
            sheet.write(0, i, u"应用")
            sheet.write(1, i, u"掉帧次数")
        tmp = k[0]
        if appMaps.get(k[0]) is not None:
            tmp = appMaps.get(k[0])
        sheet.write(0, i + 1, tmp)
        sheet.write(1, i + 1, k[1])
        i += 1
    i = 0
    for k in sortedcases:
        if i == 0:
            sheet.write(3, i, u"场景")
            sheet.write(4, i, u"掉帧次数")
        val3 = k[0]
        if caseMaps.get(k[0]) is not None:
            val3 = caseMaps.get(k[0])
        sheet.write(3, i + 1, val3)
        sheet.write(4, i + 1, k[1])
        i += 1
    sheet.insert_chart(6, 0, chart0)
    sheet.insert_chart(6, 6, chart1)
    size1 = len(sortedpkgs)
    size2 = len(sortedcases)
    chart0.add_series({
        "categories": [model, 0, 1, 0, size1],
        'values': [model, 1, 1, 1, size1],
        'line': {'color': 'red'}
    })
    chart0.set_x_axis({
        'name': u'应用',
        'name_font': {'size': 14, 'bold': True},
        'num_font': {'italic': True},
    })
    chart0.set_y_axis({
        'name': u'次数',
        'name_font': {'size': 14, 'bold': True},
        'num_font': {'italic': True},
    })
    chart0.set_size({  # 设置图表整体的大小
        'width': 400,  # 宽
        'height': 300,  # 高
    })
    chart0.set_title({  # 整个图表的标题 显示在圆柱形图上方
        'name': model + u'各应用掉帧次数',
    })
    chart1.add_series({
        "categories": [model, 3, 1, 3, size2],
        'values': [model, 4, 1, 4, size2],
        'line': {'color': 'red'}
    })
    chart1.set_x_axis({
        'name': u'场景',
        'name_font': {'size': 12, 'bold': True},
        'num_font': {'italic': True},
    })
    chart1.set_y_axis({
        'name': u'次数',
        'name_font': {'size': 12, 'bold': True},
        'num_font': {'italic': True},
    })
    chart1.set_size({
        'width': 400,  # 宽
        'height': 300,  # 高
    })
    chart1.set_title({  # 整个图表的标题 显示在圆柱形图上方
        'name': model + u'各场景掉帧次数',
    })


# 折线图
def exe_fps_chart(sheet_writer, sheet, size, name, startx, starty, endx, endy, title):
    # print "exe_fps_chart"

    chart = sheet_writer.add_chart({'type': 'line'})
    chart.add_series({
        'values': [name, startx, starty, endx, endy],
        # 'marker': {'type': 'diamond'},
        'line': {'color': 'red'}
    })
    # chart.set_x_axis({
    #     'name': u'次数',
    #     'name_font': {'size': 12, 'bold': True},
    #     'num_font': {'italic': True},
    # })
    chart.set_y_axis({
        'name': u'掉帧数',
        'name_font': {'size': 12, 'bold': True},
        'num_font': {'italic': True},
    })
    chart.set_size({
        'width': 400,  # 宽
        'height': 300,  # 高
    })
    chart.set_title({  # 整个图表的标题 显示在圆柱形图上方
        'name': title,
    })
    sheet.insert_chart(size, 0, chart)
    # print "exe_fps_chart end"


# 饼图
def exe_fps_chart2(sheet_writer, sheet, size, name, startx, starty, endx, endy, title, size2):
    # print "exe_fps_chart"

    chart = sheet_writer.add_chart({'type': 'pie', 'substyle': 'percent_stacked'})
    chart.add_series({
        "categories": [name, startx - size2, starty, startx - size2, endy],
        # "categories":u'list[:]',
        'values': [name, startx, starty, endx, endy],
        'data_labels': {'percentage': True},
        'line': {'color': 'red'}
    })
    # chart.set_x_axis({
    #     'name': u'次数',
    #     'name_font': {'size': 12, 'bold': True},
    #     'num_font': {'italic': True},
    # })
    chart.set_y_axis({
        'name': u'掉帧数',
        'name_font': {'size': 12, 'bold': True},
        'num_font': {'italic': True},
    })
    chart.set_size({
        'width': 400,  # 宽
        'height': 300,  # 高
    })
    chart.set_title({  # 整个图表的标题 显示在圆柱形图上方
        'name': title,
    })
    sheet.insert_chart(size, 0, chart)
    # print "exe_fps_chart end"


if __name__ == '__main__':
    parse_logs()
