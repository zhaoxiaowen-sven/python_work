#!/usr/bin/env python
# coding:utf-8

import os
import sys
from collections import Counter
from ftplib import FTP
import time
import xlrd
import xlsxwriter
from utils.config_utils import ConfigUtils

defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)

HOST = "192.168.15.157"
DIR = "UniversalTest/performance_ScenarioTest/"
CONFIG_DIR = "config/cases.xlsx"
RESULT_DIR = "config/result.xlsx"

# 读取配置文件
caseMaps,appMaps,deviceMaps = ConfigUtils.readConfig()

def sort_case_results():
    # 连接ftp目录
    ftp = FTP()
    ftp.set_debuglevel(0)
    ftp.connect(HOST)
    ftp.login("", "")
    ftp.cwd(DIR)
    dirs = ftp.nlst()
    # print dirs

    # 解析测试用例的父目录
    target_dirs = []
    for dirname in dirs:
        # print dirname
        if dirname.startswith("out"):
            target_dirs.append(dirname)
    # print target_dirs

    records = {}
    app_records = {}
    keys = []
    times = {}

    for target_dir in target_dirs:
        # ftp.cwd(target_dir)
        # print "======"
        values = []
        app_values = []
        key = target_dir
        # print key
        file_names = ftp.nlst(target_dir)
        # time2 = time.ctime(os.stat(target_dir+"/logcat.log").st_mtime)
        # timeStr2 = ftp.retrlines("LIST "+target_dir+"/logcat.log")
        # print timeStr2
        # print  ftp.dir(target_dir+"/logcat.log")
        # arr = timeStr2.split(" ")
        # print arr
        # print key,timeStr2
        # print file_names
        for file_name in file_names:
            if file_name.find("-") != -1:
                length = len(file_name)
                # print file_name
                # time = file_name[0:length - 5]
                # pkg = file_name[length - 4:length - 2]
                # value = file_name[length - 2:length]
                # print key, pkg, value
                # time1 = file_name.split("-")[2]
                # time2 = ftp.
                app_values.append(file_name[length - 4:length - 2])
                values.append(file_name[length - 4:length])
        if len(values) > 0 and len(app_values) > 0:
            # print key,values
            keys.append(key)
            records[key] = values
            app_records[key] = app_values
    ftp.close()

    # print records
    # print app_records
    # 统计各用例的执行次数
    records2 = {}
    app_records2 = {}
    for k in keys:
        records2[k] = dict(Counter(records.get(k)))
        app_records2[k] = dict(Counter(app_records.get(k)))
    # print records2
    # print app_records2

    # 写到目录中
    sheet_writer = xlsxwriter.Workbook(RESULT_DIR)
    i = 0
    for name in keys:
        d0 = dict(app_records2.get(name))
        d = dict(records2.get(name))

        # print d0, d
        sheet = sheet_writer.add_worksheet(name)
        chart0 = sheet_writer.add_chart({'type': 'column'})
        chart1 = sheet_writer.add_chart({'type': 'column'})

        i = 0
        point = 0
        for k1 in d0.keys():
            if i == 0:
                sheet.write(0, i, u"应用")
                sheet.write(1, i, u"次数")
            tmp = k1
            if appMaps.get(k1, "null") != "null":
                tmp = appMaps.get(k1)
            sheet.write(0, i + 1, tmp)
            sheet.write(1, i + 1, d0.get(k1))
            i += 1
            point += 1

        i = 0

        for k in d.keys():
            if i == 0:
                sheet.write(2, i, u"用例")
                sheet.write(3, i, u"次数")
            val3 = k
            if caseMaps.get(k, "null") != "null":
                val3 = caseMaps.get(k)
            sheet.write(2, i + 1, val3)
            sheet.write(3, i + 1, d.get(k))
            i += 1
            point += 1

        size1 = len(d0)
        size2 = len(d)
        sheet.insert_chart(5, 0, chart0)
        sheet.insert_chart(5, 6, chart1)
        chart0.add_series(
            {
                "categories": [name, 0, 1, 0, size1],
                'values': [name, 1, 1, 1, size1],
                'line': {'color': 'red'}
            }
        )
        chart0.set_x_axis(
            {
                'name': u'应用',
                'name_font': {'size': 14, 'bold': True},
                'num_font': {'italic': True},
            }
        )
        chart0.set_y_axis(
            {
                'name': u'次数',
                'name_font': {'size': 14, 'bold': True},
                'num_font': {'italic': True},
            }
        )
        chart0.set_size({  # 设置图表整体的大小
            'width': 400,  # 宽
            'height': 300,  # 高
        })
        chart0.set_title({  # 整个图表的标题 显示在圆柱形图上方
            'name': u'各应用异常次数',
        })

        chart1.add_series({
            "categories": [name, 2, 1, 2, size2],
            'values': [name, 3, 1, 3, size2],
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
            'name': u'各场景异常次数',
        })

    sheet_writer.close()
    print("excel make success")


# sort_case_results()

SAVE_DIR = "d:/out/"
TARGET_FILE = "debug.log"
TIME_STAMP="%Y%m%d%H%M%S"
bufsize = 1024

def ftp_download():
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
                start_time = time.mktime(time.strptime("20"+arr[2],TIME_STAMP))
                # print device , start_time

                target_dirs.append(dirname)

    print(target_dirs)

    for target_dir in target_dirs:

        try:
            arr = ftp.nlst(target_dir)
            if TARGET_FILE in arr:
                local_path = SAVE_DIR + target_dir
                if not os.path.exists(local_path):
                    os.makedirs(local_path)
                f = open(local_path + "/" + TARGET_FILE, "wb")
                server_path = "RETR " + target_dir + "/" + TARGET_FILE
                ftp.retrbinary(server_path, f.write, bufsize)
                f.close()
        except Exception as e:
            print("read " + target_dir + " error = ", e)
            continue
    ftp.quit()
ftp_download()

def process(string):
    print("process String")

