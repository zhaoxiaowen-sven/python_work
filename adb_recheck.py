#!/bin/python
# coding:utf-8

import getopt
import os
import re
import subprocess
import sys


class Adb():
    ''' 封装 ANDROID_HOME 或者 PATH 里的 adb 命令'''
    __adb_cmd = None

    def __init__(self, serial=None):
        # 默认返回 adb devices 列表第一个 device
        if serial == None:
            serial = Adb.get_devices()
            if len(serial) > 0:
                self.serial = serial[0]
        else:
            self.serial = serial

    @staticmethod
    def adb():
        if Adb.__adb_cmd == None:
            if "ANDROID_HOME" in os.environ:
                filename = "adb.exe" if os.name == 'nt' else 'adb'
                adb = os.path.join(os.environ["ANDROID_HOME"], "platform-tools", filename)
                if not os.path.exists(adb):
                    raise EnvironmentError("adb not found in $ANDROID_HOME path: %s." % os.environ["ANDROID_HOME"])
            else:
                import distutils
                if "spawn" not in dir(distutils):
                    import distutils.spawn
                adb = distutils.spawn.find_executable("adb")
                if adb:
                    adb = os.path.realpath(adb)
                else:
                    raise EnvironmentError("$ANDROID_HOME environment not set, and not found adb in $PATH.")
            Adb.__adb_cmd = adb
        return Adb.__adb_cmd

    @staticmethod
    def get_devices():
        devices = []
        start_server = [Adb.adb(), "start-server"]
        cmd_line = [Adb.adb(), "devices"]
        if os.name != "nt":
            cmd_line = [" ".join(cmd_line)]
        # 先执行 adb start-server 避免 adb devices 解析出错
        subprocess.Popen(start_server).wait()
        result = subprocess.Popen(cmd_line, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result = result.stdout.read().decode().replace('\r', '').strip('\n').split('\n')
        if len(result) == 1:
            return devices
        else:
            for d in result[1:]:
                d = d.split('\t')[0]
                devices.append(d)
        return devices

    def __process_result(self, result):
        return result.decode().replace('\r', '').strip('\n').split('\n')

    def cmd(self, *args):
        cmd_line = [self.adb(), "-s", self.serial] + list(args)
        #    for arg in args:
        #      if isinstance(arg, list):
        #        cmd_line += list(arg)
        #      elif isinstance(arg, str):
        #        cmd_line += [arg]
        if os.name != "nt":
            cmd_line = [" ".join(cmd_line)]
        return subprocess.Popen(cmd_line, shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)

    def press_home(self):
        self.cmd(["shell input keyevent KEYCODE_HOME"])

    def get_free_mem(self):
        '''获取手机剩余可用内存,单位为 M'''
        result = self.cmd(["shell cat /proc/meminfo"])
        result = self.__process_result(result.stdout.read())
        memfree = self.grep("MemFree", result)[0].split()[1]
        buffers = self.grep("Buffers", result)[0].split()[1]
        cached = self.grep("Cached", result)[0].split()[1]
        free = int(memfree) + int(buffers) + int(cached)
        return free / 1024

    def get_total_mem(self):
        '''获取手机总内存,单位为M'''
        result = self.cmd(["shell cat /proc/meminfo"])
        result = self.__process_result(result.stdout.read())
        memtotal = self.grep("MemTotal", result)[0].split()[1]
        return int(memtotal) / 1024

    def start_app(self, package):
        '''打开手机指定包名的应用'''
        self.cmd(["shell monkey -p %s -c android.intent.category.LAUNCHER 1" % package]).wait()

    def get_launch_time(self, package, activity):
        '''获取指定应用 activity 的启动时间'''
        result = self.cmd(["shell am start -W %s/%s" % (package, activity)])
        result = self.__process_result(result.stdout.read())
        try:
            thisTime = int(self.grep("ThisTime", result)[0].split()[1])
            totalTime = int(self.grep("TotalTime", result)[0].split()[1])
            waitTime = int(self.grep("WaitTime", result)[0].split()[1])
        except IndexError:
            print(package)
            print(result)
        return [thisTime, totalTime, waitTime]

    def stop_app(self, package):
        '''强制停止指定应用'''
        self.cmd(["shell am force-stop %s" % package]).wait()

    def get_product_name(self):
        '''获取手机名称'''
        result = self.cmd(["shell getprop ro.product.model"])
        result = self.__process_result(result.stdout.read())[0]
        return result

    def get_os_version(self):
        '''获取手机的android版本号'''
        result = self.cmd(["shell getprop ro.build.version.release"])
        result = self.__process_result(result.stdout.read())[0]
        return result

    def get_product_brand(self):
        '''获取手机厂商'''
        result = self.cmd(["shell getprop ro.product.brand"])
        result = self.__process_result(result.stdout.read())[0]
        return result

    def get_pids(self, package):
        '''获取应用 pid 和对应进程名'''
        result = {}
        ps = self.cmd(["shell ps"]).communicate()[0].decode().split(os.linesep)
        # print(package)
        user = self.grep(package, ps)
        if len(user) > 0:
            user = user[0].split()[0]
        else:
            return result
        PS = r'({})\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'.format(user)

        for line in ps:
            match = re.search(PS, line)
            if match:
                pid = match.group(2)
                ppid = match.group(3)
                name = match.group(9)
                # if(name.find(package) !=-1):
                result[pid] = name+"(pid = "+str(pid)+",ppid = "+str(ppid)+")"
        # print("result = ",result)
        return result

    def get_adj(self, pid):
        '''获取 pid 对应的优先级'''
        result = self.cmd(["shell cat /proc/%s/oom_adj" % pid])
        adj = result.communicate()[0].decode().strip('\n').strip('\r')
        if "system" in adj:
            adj = "none"
        return adj

    def get_adjs(self, pids):
        '''获取 pids 的优先级'''
        adjs = {}
        for pid in pids:
            name = pids[pid]
            adjs[name] = self.get_adj(pid)
        return adjs

    def get_score_adj(self, pid):
        '''获取 pid 对应的score_adj优先级'''
        result = self.cmd(["shell cat /proc/%s/oom_score_adj" % pid])
        adj = result.communicate()[0].decode().strip('\n').strip('\r')
        # if "system" in adj:
        #     adj = "none"
        return adj

    def get_score_adjs(self, pids):
        '''获取 pids 的优先级'''
        adjs = {}
        for pid in pids:
            name = pids[pid]
            adjs[name] = self.get_score_adj(pid)
        return adjs


    def get_cpus(self, pids):
        '''获取 pids 的 cpu 使用率'''
        result = self.cmd(["shell top -n 1"])
        # print("result = ", result.communicate()[0].decode())
        result = result.communicate()[0].decode().strip('\n').strip('\r')
        # print(result)
        # result = result.communicate()[0].read().decode().strip('\n').strip('\r')
        result = result.split(os.linesep)
        cpus = {}
        for pid in pids.keys():
            TOP = r'({})\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)'.format(pid)
            name = pids[pid]
            # name = pid
            # print("pid = ", pid)
            cpus[name] = 'none'
            for line in result:
                match = re.search(TOP, line)
                if match:
                    # print("line = " + line)
                    if self.get_os_version().startswith("7"):
                        cpus[name] = match.group(5)
                    else:
                        cpus[name] = match.group(3)
                    # print("name=", name, "cpu=" + cpus[name])
                    cpus[name] = cpus[name].strip('%')

        return cpus

    def grep(self, search_re, source):
        '''
        模拟 Unix 工具 grep
        :param search_re: 要搜索的字段
        :param source: 搜索源，应该是列表
        '''
        result = []
        for line in source:
            # print("line", line)
            if re.search(search_re, line):
                result.append(line)
        # print(result)
        return result

if __name__ == "__main__":
    adb = Adb()

    def get_info(pkgname):
        pids = adb.get_pids(pkgname)
        print(u"=====应用各进程的pid=====")
        print(pids)

        print(u"=== 应用各进程的adj值（oom_score_adj<500即为异常值） ===")
        adjs = adb.get_score_adjs(pids)
        for k, v in adjs.items():
            # if int(v) < 5:
            print(k, " = ", v)

        print(u"=== 应用各进程的cpu占用率（>5%即为异常值）===")
        cpus = adb.get_cpus(pids)
        for k, v in cpus.items():
            # if int(v) > 5:
            print(k, " = ", v)

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:")
        print(sys.argv[0])
    except getopt.GetoptError as e:
        print(e)

    for opt, arg in opts:
        if opt == '-h':
            print("please input -p with a package name")
        elif opt == '-p':
            pkgname = arg
            get_info(pkgname)
