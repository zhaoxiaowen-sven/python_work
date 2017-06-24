#!/usr/bin/env python
# coding:utf-8
import xlrd

# 测试相关的配置信息
# 1.场景编码 2.应用编码 3.设备编码
CONFIG_DIR = "E:/Project/Pycharm/ftp_work/config/cases.xlsx"
SHEET_CASE_CODE = "case_code"
SHEET_APP_CODE = "app_code"
SHEET_DEVICE_CODE = "device_code"

class ConfigUtils:
    @staticmethod
    def readConfig():
        readData = xlrd.open_workbook(CONFIG_DIR)

        caseMaps = ConfigUtils.readsheet(readData, SHEET_CASE_CODE)
        appMaps = ConfigUtils.readsheet(readData, SHEET_APP_CODE)
        deviceMaps = ConfigUtils.readsheet(readData, SHEET_DEVICE_CODE)

        return caseMaps, appMaps, deviceMaps

    @staticmethod
    def readsheet(readData, sheetname):
        table = readData.sheet_by_name(sheetname)
        d = {}
        index = 0
        while index < table.nrows:
            val1 = table.row(index)[0].value
            val2 = table.row(index)[1].value
            if len(val1) != 0 or len(val2) != 0:
                d[val2] = val1
            index += 1
        return d

# caseMaps,appMaps,deviceMaps = ConfigUtils.readConfig()

# print caseMaps,appMaps,deviceMaps