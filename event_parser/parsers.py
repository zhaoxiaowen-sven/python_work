#!/usr/bin/env python
# coding:utf-8
import re

from dateutil.parser import parse

RESUME_PATTERN = r"(.*)\s+\d+\s+\d+ I am_resume_activity: \[(\d+,){3}(.*)/(.*)\]"
RESUME_PATTERN = r"(.*)\s+\d+\s+\d+ I am_resume_activity: \[(\d+,){3}(.*)/(.*)\]"
FOCUSED_PATTERN = r".* am_focused_activity: \[\d+,(.*)/.*\]"
CRASH_PATTERN = r"(.*)\s+\d+\s+\d+ I am_crash: \[(\d+,){2}(.*),\d+,.*\]"
ANR_PATTERN = "(.*)\s+\d+\s+\d+ I am_anr: \[(\d+,){2}(.*),\d+,.*\]"
SCREEN_PATTERN = "(.*)\s+\d+\s+\d+ I screen_toggled: (\d+)"

START_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_start: \[(\d+,){3}(.*),(.*),.*\]"
BOUND_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_bound: \[(\d+,){2}(.*)\]"


class Parser(object):
    def __init__(self):
        # print("")
        self.name = "parser"

    def parse(self):
        # print("")
        self.name = "parser"

    def comparetime(self, time1, time2):
        return (parse(time2) - parse(time1)).total_seconds() * 1000


class ResumeParser(Parser):
    def parse(self, line, temp_resume):
        match_resume = re.search(RESUME_PATTERN, line)
        time = match_resume.group(1)
        time = time[6:-5]
        # print "time", time
        pkgname = match_resume.group(3)
        activity = match_resume.group(4)
        if pkgname in temp_resume.keys():
            v = temp_resume.get(pkgname)
            v[0] += 1
            if activity in v[1].keys():
                count_a = v[1].get(activity)
                count_a += 1
                v[1][activity] = count_a
            else:
                v[1][activity] = 1
            v[2].append(time)
            temp_resume[pkgname] = v
        else:
            temp_resume[pkgname] = [1, {activity: 1}, [time]]


class AnrParser(Parser):
    def parse(self, line, temp_anr):
        match_anr = re.search(ANR_PATTERN, line)
        time = match_anr.group(1)
        time = time[6:-5]
        pkgname = match_anr.group(3)
        # temp_anr = result.get('anr')
        if pkgname in temp_anr.keys():
            v = temp_anr.get(pkgname)
            v += 1
            temp_anr[pkgname] = v
        else:
            temp_anr[pkgname] = [1, [time]]


class CrashParser(Parser):
    def parse(self, line, temp_crash):
        match_crash = re.search(CRASH_PATTERN, line)
        time = match_crash.group(1)
        time = time[6:-5]
        pkgname = match_crash.group(3)
        # temp_crash = result.get("crash")
        if pkgname in temp_crash.keys():
            v = temp_crash.get(pkgname)
            v[0] += 1
            v[1].append(time)
        else:
            temp_crash[pkgname] = [1, [time]]


class ScreenParser(Parser):
    def parse(self, length, line, lines, temp_screen, temp_screen_focused, x):
        match_screen = re.search(SCREEN_PATTERN, line)
        time = match_screen.group(1)
        time = time[6:-5]
        state = match_screen.group(2).strip()
        if state in temp_screen.keys():
            v = temp_screen.get(state)
            v[0] += 1
            v[1].append(time)
            # temp_screen[state] =
        else:
            temp_screen[state] = [1, [time]]
        if state == '1':  # 计算亮屏后打开的第一个activity
            # point = f.tell()
            for i in range(1, 10):
                if x + i >= length:
                    break
                # line_focused = f.readline()
                line_focused = lines[x + i]
                match_tmp = re.match(SCREEN_PATTERN, line_focused)
                if match_tmp and match_tmp.group(2).strip() == 1:
                    break
                # match_focused = re.search(FOCUSED_PATTERN, line_focused)
                match_focused = re.search(FOCUSED_PATTERN, line_focused)
                if match_focused:
                    pkgname = match_focused.group(1).strip()
                    # temp_screen_resume
                    temp_screen_focused["count"] += 1
                    if pkgname in temp_screen_focused:
                        temp_screen_focused[pkgname] += 1
                    else:
                        temp_screen_focused[pkgname] = 1
                    break


class ProcParser(Parser):
    def parse(self, length, line, lines, temp_proc, x):
        match_start = re.search(START_PATTERN, line)
        # 找到start_proc的地方,比较位置
        for j in range(1, 10):
            if x + j >= length:
                break
            line_bound = lines[x + j]
            match_bound = re.search(BOUND_PATTERN, line_bound)
            if match_bound:
                timestr1 = match_start.group(1)
                procname1 = match_start.group(3)
                timestr2 = match_bound.group(1)
                procname2 = match_bound.group(3)
                if procname2 == procname1:  # and len(timestr1) == len(timestr2):
                    # if procname2 == "com.android.bluetooth":
                    # print "======", timestr1, timestr2
                    try:
                        tmp = self.comparetime(timestr1, timestr2)
                        if tmp > 100:
                            break
                        if procname2 in temp_proc.keys():
                            l = temp_proc.get(procname2)
                            l[1].append(timestr1)
                            l[0].append(tmp)
                        else:
                            temp_proc[procname2] = [[tmp], [timestr1]]
                            break
                    except Exception as e:
                        print(e, procname2, timestr1, timestr2)
                        # print line
                        # print line2
                        # flag = 1
                        break
