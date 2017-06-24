#!/usr/bin/env python
# coding:utf-8
import datetime
import time
TIME_STAMP = "%Y%m%d%H%M%S"

class TimeUtils:
    # @staticmethod
    # def comparetime(targettime, *time):
    #     if len(time) == 1:
    #         return TimeUtils.comparetime1(targettime, time[0])
    #     elif len(time) == 2:
    #         return TimeUtils.comparetime2(targettime, time[0], time[1])
    #     else:
    #         # print "时间参数有误"
    #         raise Exception("时间参数有误")

    @staticmethod
    def comparetime1(targettime, begintime):
        if targettime - begintime > 0:
            return True
        else:
            return False

    @staticmethod
    def comparetime2(targettime, begintime, endtime='0'):
        targettime = TimeUtils.str2stamp(targettime, TIME_STAMP)
        begintime = TimeUtils.str2stamp(begintime, TIME_STAMP)
        if endtime == '0':
            return TimeUtils.comparetime1(targettime, begintime)
        endtime = TimeUtils.str2stamp(endtime, TIME_STAMP)

        if(begintime >= endtime):
            raise Exception("参数错误，开始时间必须小于结束时间")

        if targettime - begintime > 0 and endtime - targettime > 0:
            return True
        else:
            return False

    @staticmethod
    def str2stamp(time1, formatter):
        return time.mktime(time.strptime(time1, formatter))

    @staticmethod
    def getTodayTimeStamp():
        time_stamp = datetime.datetime.now().strftime("%Y-%m-%d")

        return time_stamp
