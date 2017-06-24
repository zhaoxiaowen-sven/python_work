#!/usr/bin/env python
# coding:utf-8
import subprocess
import threading
import time

cmd0 = "setprop debug.choreographer.skipwarning 10"
cmd1 = "stop"
cmd2 = "start"
cmd3 = "getprop debug.choreographer.skipwarning"
# adb install -r Systrace.apk
# adb shell am startservice com.mushroom.systrace/.LogService
# adb shell am startservice com.mushroom.systrace/.TraceService
# adb install -r mushroom.test.cases.apk
# adb install -r mushroom.test.cases.test.apk
cmd4 = " install -r mushroom.test.cases.apk"
cmd5 = " install -r mushroom.test.cases.test.apk"
cmd6 = " install -r Systrace.apk"
cmd7 = " shell am startservice com.mushroom.systrace/.LogService"
cmd8 = " shell am startservice com.mushroom.systrace/.TraceService"

def list_devices():
    p = exec_shell("adb devices", False)
    out = p.stdout.read().decode()
    # print "out", out
    out = out.replace('\r', '').strip('\n').split('\n')
    devices = []
    print("----------------------------")
    print("List of devices attached")
    for i in range(1, len(out)):
        print(out[i])
        devices.append(out[i].split()[0])
    print("----------------------------")
    return devices


def exec_shell(cmd, with_shell=False):
    p = subprocess.Popen(cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=with_shell)
    return p


def set_prop(device):
    # exec_shell("adb -s " + device + "vivoroot").communicate()
    exec_shell("adb -s " + device + " shell " + cmd0).communicate()
    exec_shell("adb -s " + device + " shell " + cmd1).communicate()
    exec_shell("adb -s " + device + " shell " + cmd2).communicate()
    # print exec_shell("adb -s " + device + "shell " + cmd3).stdout.read().decode()
    # print exec_shell()


def exec_cmds(devices, method_name):
    print("===========exec_cmds start===========")
    start = time.time()
    threads = []
    for i in range(len(devices)):
        t = threading.Thread(target=method_name, args=(devices[i],))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print("device(s) number: " + str(len(devices)))
    print("==========exec_cmds completed!==========")
    end = time.time() - start
    print("used time: %.1f s" % end)

def get_prop(devices):
    print('============== getprop begin =============')
    for i in devices:
        p = exec_shell("adb -s " + i + " shell " + cmd3)
        out = p.stdout.read().decode()
        out = out.replace('\r', '').strip('\n').split('\n')
        print(i+" prop is", out)
    print('============== getprop end   ===============')


def install_apk(devices):
    print('============== install apk begin =============')
    for i in devices:
        exec_shell("adb -s " + i + cmd4).communicate()
        exec_shell("adb -s " + i + cmd5).communicate()
        exec_shell("adb -s " + i + cmd6).communicate()
        exec_shell("adb -s " + i + " shell " + cmd7).communicate()
        exec_shell("adb -s " + i + " shell " + cmd8).communicate()
    print ('============== install apk end ===============')

if __name__ == '__main__':
    devices = list_devices()
    exec_cmds(devices, set_prop)
    get_prop(devices)
    # exec_cmds(devices, install_apk)


