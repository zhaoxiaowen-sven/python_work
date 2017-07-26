#!/usr/bin/env python
# coding:utf-8
import re

from dateutil.parser import parse

# 用户行为相关
RESUME_PATTERN = r"(.*)\s+\d+\s+\d+ I am_resume_activity: \[(\d+,){3}(.*)/(.*)\]"
RESUME_CALLED_PATTERN = r"(.*)\s+\d+\s+\d+ I am_on_resume_called: \[\d,(.*)\]"
FOCUSED_PATTERN = r".* am_focused_activity: \[\d+,(.*)/.*\]"
# 异常相关
CRASH_PATTERN = r"(.*)\s+\d+\s+\d+ I am_crash: \[(\d+,){2}(.*),\d+,.*\]"
ANR_PATTERN = "(.*)\s+\d+\s+\d+ I am_anr\s+:\s+\[(\d+,){2}(.*),\d+,.*\]"

SCREEN_PATTERN = "(.*)\s+\d+\s+\d+ I screen_toggled: (\d+)"
# 进程启动相关
START_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_start: \[\d+,(\d+),\d+,(.*),(.*),.*\]"
BOUND_PATTERN = r"(.*)\s+\d+\s+\d+ I am_proc_bound: \[\d+,(\d+),(.*)\]"
# 内存
PSS_PATTERN = r"(.*)\s+\d+\s+\d+ I am_pss  : \[\d+,\d+,([^,]+),(\d+),(\d+)(,\d+)?\]"
MEM_PATTERN = r"(.*)\s+\d+\s+\d+ I am_meminfo: \[(\d+),(\d+),(\d+),(\d+),(\d+)\]"

# 杀进程相关
KILL_PATTERN = r"(.*)\s+\d+\s+\d+ I am_kill : \[\d+,\d+,([^,]+),(\d+),.*\]"

# 电池电量
BATTERY_PATTERN = r'(.*)\s+\d+\s+\d+ I battery_level: \[(\d+),(\d+),(\d+)\]'

# 启动的时间
LAUNCH_PATTERN = r'(.*)\s+\d+\s+\d+ I am_activity_launch_time:\s+\[\d+,\d+,(.*),(\d+),(\d+)\]'

BBK_LANUCHER = "com.bbk.launcher2"

top10app = ["com.tencent.mobileqq", "com.qiyi.video", "com.tencent.karaoke", "com.tencent.mm", "com.kugou.android",
            "com.tencent.qqlive", "com.eg.android.AlipayGphone", "com.taobao.taobao", "com.baidu.searchbox",
            "com.smile.gifmaker"]


class Parser(object):
    def __init__(self):
        # print("")
        self.name = "parser"

    def parse(self):
        # print("")
        self.name = "parser"

    def comparetime(self, time1, time2):
        return (parse(time2) - parse(time1)).total_seconds() * 1000

    def is_top10_process(self, process):
        flag = False
        for name in top10app:
            if process.find(name) != -1:
                flag = True
                break
        return flag


class LauncherParser(Parser):
    def parse(self, line, temp_launch):
        match_launch = re.search(LAUNCH_PATTERN, line)
        if match_launch:
            time = match_launch.group(1).strip()
            ui = match_launch.group(2)
            start = match_launch.group(3)
            total = match_launch.group(4)
            # print(time, ui, start, total)

            temp_launch.get("time").append(time)
            temp_launch.get("ui").append(ui)
            temp_launch.get("start").append(start)
            temp_launch.get("total").append(total)

            # pass


class BatteryParser(Parser):
    def parse(self, line, temp_battery):
        match_battery = re.search(BATTERY_PATTERN, line)
        if match_battery:
            time = match_battery.group(1).strip()
            level = match_battery.group(2)
            voltage = match_battery.group(3)
            T = match_battery.group(4)

            # print(time, level, voltage, T)

            temp_battery.get("time").append(time)
            temp_battery.get("level").append(level)
            temp_battery.get("voltage").append(voltage)
            temp_battery.get("T").append(T)


class MemParser(Parser):
    def parse(self, line, temp_mem):
        match_mem = re.search(MEM_PATTERN, line)
        if match_mem:
            time = match_mem.group(1).strip()
            # 修改之后可能有bug，原始数据最好不要修改，处理的时候再修改
            # time = time[6:-5]

            cached = match_mem.group(2)
            free = match_mem.group(3)
            zram = match_mem.group(4)
            kernel = match_mem.group(5)
            native = match_mem.group(6)
            # print(time, cached, free, zram, kernel, native)

            temp_mem.get("time").append(time)
            temp_mem.get("cached").append(cached)
            temp_mem.get("free").append(free)
            temp_mem.get("zram").append(zram)
            temp_mem.get("kernel").append(kernel)
            temp_mem.get("native").append(native)

            # pass


class KillParser(Parser):
    def parse(self, line, temp_kill):
        match_kill = re.search(KILL_PATTERN, line)
        if match_kill:
            # print(222)
            time = match_kill.group(1)
            process = match_kill.group(2)
            oom_adj = match_kill.group(3)
            flag = self.is_top10_process(process)
            if not flag:
                return
            if process in temp_kill.keys():
                temp_kill[process] += 1
            else:
                temp_kill[process] = 1
                # pass


class PssParser(Parser):
    def parse(self, line, temp_pss):
        # print(line)
        match_pss = re.search(PSS_PATTERN, line)
        if match_pss:
            # print("111")
            time = match_pss.group(1)
            process = match_pss.group(2)
            pss = match_pss.group(3)
            uss = match_pss.group(4)
            # print(time, process, pss, uss)
            flag = self.is_top10_process(process)
            if not flag:
                return

            if process in temp_pss.keys():
                # temp_pss[process][0].apeend(pss)
                # temp_pss[]
                v = temp_pss.get(process)
                v[0].append(pss)
                v[1].append(uss)
            else:
                temp_pss[process] = [[pss], [uss]]

                # pass


class ResumeParser(Parser):
    def parse(self, line, temp_resume, point, lines, temp2, temp3):
        match_resume = re.search(RESUME_PATTERN, line)
        if match_resume:
            time = match_resume.group(1).strip()
            # print("time", time)
            # time_special = time[6:-5]
            # print("time", time)
            pkgname = match_resume.group(3)
            activity = match_resume.group(4)
            # if pkgname not in top10app:
            #     return
            # if pkgname == BBK_LANUCHER:
            #     return
            temp3['pkg'].append(pkgname)
            temp3['time'].append(time)
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
            # 计算resume -> resume_called 的时间
            for x in range(10):
                if point + x < len(lines):
                    match_resume2 = re.search(RESUME_CALLED_PATTERN, lines[point + x])
                    if match_resume2:
                        time2 = match_resume2.group(1)
                        ui = match_resume2.group(2)

                        if ui == pkgname + activity:
                            interval = self.comparetime(time, time2)
                            # print(ui, interval)
                            temp2["time"].append(time)
                            temp2["ui"].append(ui)
                            temp2["interval"].append(interval)
                            # if ui in temp2.keys():
                            #     v = temp2.get(ui)
                            #     v[0].append(time)
                            #     v[1].append(interval)
                            # else:
                            #     temp2[ui] = [[time], ui [interval]]
                            break


class AnrParser(Parser):
    def parse(self, line, temp_anr):
        match_anr = re.search(ANR_PATTERN, line)
        if match_anr:
            # print("1111")
            time = match_anr.group(1)
            time = time[6:-5]
            pkgname = match_anr.group(3)
            # temp_anr = result.get('anr')
            if pkgname in temp_anr.keys():
                v = temp_anr.get(pkgname)
                v[0] += 1
                v[1].append(time)
                # temp_anr[pkgname] = v
            else:
                temp_anr[pkgname] = [1, [time]]


class CrashParser(Parser):
    def parse(self, line, temp_crash):
        match_crash = re.search(CRASH_PATTERN, line)
        if match_crash:
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
    def parse(self, length, line, lines, temp_screen, temp_screen_focused, x, resume4):
        match_screen = re.search(SCREEN_PATTERN, line)
        if match_screen:

            time = match_screen.group(1).strip()
            # time = time[6:-5]
            state = match_screen.group(2).strip()

            # 将亮灭屏的信息加入到resume 中，用户计算应用的使用时间
            if int(state) == 0:
                resume4['time'].append(time)
                resume4['pkg'].append(state)

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
        # start_proc 中提取出的信息
        timestr1 = match_start.group(1).strip()
        pidname1 = match_start.group(2)
        procname1 = match_start.group(3)
        #  去top10
        # flag = self.is_top10_process(procname1)
        # if not flag:
        #     return

        # 找到start_proc的地方,比较位置
        for j in range(1, 10):
            if x + j >= length:
                break
            line_bound = lines[x + j]
            match_bound = re.search(BOUND_PATTERN, line_bound)
            if match_bound:
                # bound_proc 中提取出的信息
                timestr2 = match_bound.group(1).strip()
                pidname2 = match_bound.group(2)
                procname2 = match_bound.group(3)

                # print('timestr2', timestr2, 'timestr1',timestr1)
                # print('pidname1 = ', pidname1, 'pidname2 = ', pidname2)
                if procname2 == procname1 and pidname1 == pidname2:  # and len(timestr1) == len(timestr2):
                    # if procname2 == "com.android.bluetooth":
                    # print "======", timestr1, timestr2
                    try:
                        tmp = self.comparetime(timestr1, timestr2)
                        # if tmp > 100:
                        #     break
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
