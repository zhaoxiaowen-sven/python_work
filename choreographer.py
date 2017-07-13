#!/bin/python
# coding:utf-8
__author = 'zhaoxiaowen'

import os
import re

import xlsxwriter

path = "D:/te/"
# 07-13 09:29:24.014  1423 15264 D VivoPerfService: 1030_3: com.jingdong.app.mall/.MainFrameActivity#31#14963#com.jingdong.app.mall
pattern = r"(.*)\s+\d+\s+\d+ D VivoPerfService: 1030_3: (\S+)#(\d+)#(\d+)#(\S+)"

filepaths = []
for dirpath, dirnames, filenames in os.walk(path):
    for file in filenames:
        if file.startswith("main_log"):
            filepaths.append(os.path.join(dirpath, file))

print(filepaths)
d0 = {}
for f in filepaths:
    with open(f, encoding="utf-8") as f1:
        while True:
            try:
                line = f1.readline()
                if line.find("VivoPerfService") != -1:
                    match_obj = re.search(pattern, line)
                    if match_obj:
                        time = match_obj.group(1)
                        process = match_obj.group(2)
                        frame = match_obj.group(3)
                        pkg = match_obj.group(5)
                        print(time, process, frame, pkg)

                        if pkg in d0.keys():
                            v = d0.get(pkg)
                            v[0] += 1
                            v[1].append(frame)
                            d0[pkg] = v
                        else:
                            d0[pkg] = [1, [frame]]
            except Exception as e:
                print(line)
            if not line:
                break

print(d0)
d0_sort = sorted(d0.items(), key=lambda d: d[1][0], reverse=True)
wb = xlsxwriter.Workbook("choreographer.xlsx")
sheet1 = wb.add_worksheet("times")
sheet2 = wb.add_worksheet("details")
sheet1.write(0, 0, "Pkg")
sheet1.write(0, 1, "Times")
i = 1
for v in d0_sort:
    sheet1.write(i, 0, v[0])
    sheet1.write(i, 1, v[1][0])
    i += 1
i = 0
for v in d0_sort:
    sheet2.write(0, i, v[0])
    l = v[1][1]
    print("xxx",l)
    for x in range(len(l)):
        sheet2.write(x+1, i, l[x])
    i += 1
wb.close()
