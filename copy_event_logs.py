#!/usr/bin/env python
# coding:utf-8

import os
import shutil

rootdir = "D:/log/PD1610"
target_dir = "D:/log2/eventlog/"
def copy_event_log():

    event_log_dir = []
    for root, dirs, files in os.walk(rootdir):
        # print("=====root=====")
        # print(root)
        # print("=====dirs=====")
        for d in dirs:
            pass
            # print(os.path.join(root, d))
        # print("=====files======")
        for f in files:
            if f == "events_log":
                # print(os.path.join(root, f))
                event_log_dir.append(os.path.join(root, f))
        pass

    print(event_log_dir)

    for dir in event_log_dir:
        imei = (dir.split("IMEI")[1]).split("Version")[0]
        filename = (dir.split("adb_log\\")[1]) #.split(r"\events")[0]
        print(imei, filename)
        temp = target_dir+imei+"/"+filename+"/"
        if not os.path.exists(temp):
            os.makedirs(temp)

        shutil.copy(dir, temp)

copy_event_log()