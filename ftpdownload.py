#!/usr/bin/env python
# coding:utf-8
import os
from ftplib import FTP

from utils.config_utils import ConfigUtils
from utils.time_utils import TimeUtils

SAVE_DIR = "logs/"
DEBUG_LOG = "debug.log"
EVENT_LOG = "event.log"

TIME_STAMP = "%Y%m%d%H%M%S"
# HOST = "192.168.15.157"
HOST = "172.25.105.226"
DIR = "UniversalTest/performance_ScenarioTest/"
BUFFER_SIZE = 1024
# today = TimeUtils.getTodayTimeStamp()
caseMaps, appMaps, deviceMaps = ConfigUtils.readConfig()


class FtpDownload:
    def __init__(self):
        print('init')
        self.ftp = FTP()

    def __connect(self, host, debuglevel):
        print('connect')
        self.ftp.set_debuglevel(debuglevel)
        self.ftp.connect(host)
        self.ftp.login("", "")

    def download(self, host, root, start_time, end_time='0'):
        print('download')
        # self.connect()
        self.__connect(host, 0)
        self.ftp.cwd(root)
        dirs = self.ftp.nlst()
        target_dirs = self.__get_target_dir(dirs, start_time, end_time)
        for target_dir in target_dirs:
            try:
                arr = self.ftp.nlst(target_dir)
                if DEBUG_LOG in arr:
                    self.__real_download(target_dir, DEBUG_LOG, "debug")

                if EVENT_LOG in arr:
                    self.__real_download(target_dir, EVENT_LOG, "event")

            except Exception as e:
                print("read " + target_dir + " error = ", e)
                continue
        self.ftp.quit()
        print("ftp_download finish")

    def __get_target_dir(self, dirs, start_time, end_time='0'):
        # 解析测试用例的父目录,将需要保存的目录下载到本地
        target_dirs = []
        for dirname in dirs:
            # print dirname
            if dirname.startswith("out"):
                arr = dirname.split("-")
                if len(arr) == 3:
                    time1 = "20" + arr[2]
                    if TimeUtils.comparetime2(time1, start_time, end_time):
                        target_dirs.append(dirname)
        # print target_dirs
        return target_dirs
        # 生成本地文件的目录

    def __make_local_path(self, target_dir, dir_name):
        arrs = target_dir.split("-")
        device = arrs[1]
        time = arrs[2][:len(arrs[2]) - 6]
        value = deviceMaps.get(device)
        local_path = SAVE_DIR
        # 找到对应的机型
        if value is not None:
            # target_dir = value
            local_path = SAVE_DIR + value + "/" + time + "/" + dir_name + "/"
        if not os.path.exists(local_path):
            os.makedirs(local_path)
        return local_path

    # 从服务器上下载
    def __real_download(self, target_dir, log_name, dir_name):
        local_path = self.__make_local_path(target_dir, dir_name)
        file_path = local_path + target_dir + "_" + log_name
        f = open(file_path, "wb")
        server_path = "RETR " + target_dir + "/" + log_name
        self.ftp.retrbinary(server_path, f.write, BUFFER_SIZE)
        f.close()


if __name__ == '__main__':
    ftp_download = FtpDownload()
    ftp_download.download(HOST, DIR, "20170605171800")
