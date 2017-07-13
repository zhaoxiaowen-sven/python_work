# coding:utf-8
__author__ = 'wumingyue'

import argparse
import os
import sys
import time

from adb import Adb
from vivotools import VivoTests, VivoTools, VivoReport, VivoGlobals, TestCase

FAIL_REPORT = "D:/AutoTest/UniversalTest/performance_CommonTest/failReport/fail_report.txt"

PATH = lambda p: os.path.abspath(
    os.path.join(os.path.dirname(__file__), p)
)
# VivoTests.DownApk 必须用相对路径才能下载成功
DOWNLOAD_DIR = os.path.join("..", "download")


class CommonTest(TestCase):
    def setUp(self):
        super(CommonTest, self).setUp()
        VivoTools.LOGD("performance", u"setUp ...")
        self.adb = Adb(VivoGlobals.g_thread_data.local_desired_caps['udid'])
        VivoReport.Todo(VivoReport.WebReport.DOWNLOAD_APP)
        self.parseArgs()
        # 这里 localDir 要用相对路径
        if VivoTests.DownApk(self.apkUrl, localDir=DOWNLOAD_DIR):
            VivoReport.Passed()
        else:
            VivoTools.WriteErrType(strText=" FAIL @ " \
                                           + VivoReport.WebReport.idof(VivoReport.WebReport.DOWNLOAD_APP))
            VivoReport.BugReport(VivoReport.WebReport.DOWNLOAD_APP + " FAIL", \
                                 VivoReport.WebReport.idof(VivoReport.WebReport.DOWNLOAD_APP), comment=self.apkUrl)
            VivoReport.Finish()
            VivoGlobals.g_is_testcase_exit = True
            sys.exit(0)
            # 结束
        self.appInfo = VivoTools.parseApkInfo(self.getApkPath())
        VivoTools.LOGD("performance", u"getApkPath ..." + self.getApkPath())
        VivoTools.LOGD("performance", self.appInfo)
        self.desired_caps['appPackage'] = self.appInfo['name']
        self.desired_caps['app'] = self.getApkPath()
        self.desired_caps['appActivity'] = \
            VivoTools.getActivity(self.appInfo['name']) \
                if self.appInfo['launchableActivity'] == None \
                else self.appInfo['launchableActivity']
        VivoTools.disableRetry()
        self.driver.mDevice.watcher(u"权限").when(text=u"权限请求") \
            .click(text="允许")

    def tearDown(self):
        super(CommonTest, self).tearDown()
        self.driver.quit()

    def parseArgs(self):
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument("--apkpath", help="Test app url")
        caseargs = arg_parser.parse_args(self.desired_caps['caseargs'].split())
        self.apkUrl = "" if caseargs.apkpath == None else caseargs.apkpath

    def getApkPath(self):
        '''获取下载测试应用的绝对路径'''
        return PATH(os.path.join(DOWNLOAD_DIR, self.apkUrl.split('/').pop()))

    def homeQuit(self, package):
        count = 4
        while count > 0 and VivoTools.isInPackage(package):
            self.driver.keyHome()
            count = count - 1
        if VivoTools.isInPackage(package):
            VivoReport.BugReport(u"无法 HOME 后台", "test", \
                                 u"自动 HOME 后台应用出现问题", self.getApkPath(), module=self.desired_caps['appPackage'])
            VivoTools.captureScreen()
            return False
        return True

    # To do: 点击图片的确定框
    def backQuit(self, package):
        # self.driver.press() 有 3 秒延迟
        self.driver.mDevice.press.back()
        self.driver.mDevice.press.back()
        self.driver.mDevice.press.back()
        self.driver.mDevice.press.back()
        try:
            if VivoTools.isInPackage(package):
                self.driver.mDevice.press.back()
                clicks = self.driver.mDevice(clickable=True, checked=False)
                count = clicks.count
                for i in range(0, count):
                    clicks[i].click()
                    if not VivoTools.isInPackage(package):
                        break
                    self.driver.mDevice.press.back()
        except:
            VivoTools.LOGE("performance", sys.exc_info()[0])
        if VivoTools.isInPackage(package):
            VivoReport.BugReport(u"无法 BACK 后台", "test", \
                                 u"自动 BACK 后台应用出现问题", self.getApkPath(), module=self.desired_caps['appPackage'])
            VivoTools.captureScreen()
            return False
        return True

    def checkHomeAdj(self, home_adjs):
        '''HOME 后台后的应用优先级应该大于 5'''
        VivoTools.LOGD("performance", u"checkHomeAdj ..." + str(home_adjs))
        report = False
        for key in home_adjs:
            adj = home_adjs[key]
            if adj != "none" and int(adj) < 5:
                report = True
                break
        if report:
            VivoTools.LOGD("performance", u"HOME 后台优先级异常")
            VivoTools.LOGD("performance", home_adjs)
            VivoReport.BugReport(u"HOME 后台优先级异常", "adj", str(home_adjs), self.getApkPath(),
                                 module=self.desired_caps['appPackage'])
            return False
        return True

    def checkBackAdj(self, back_adjs):
        '''BACK 后台后的应用优先级应该大于 9'''
        VivoTools.LOGD("performance", u"checkBackAdj ...")
        report = False
        for key in back_adjs:
            adj = back_adjs[key]
            if adj != "none" and int(adj) < 9:
                report = True
        if report:
            VivoTools.LOGD("performance", u"BACK 后台优先级异常")
            VivoTools.LOGD("performance", back_adjs)
            VivoReport.BugReport(u"BACK 后台优先级异常", "adj", str(back_adjs), self.getApkPath(),
                                 module=self.desired_caps['appPackage'])
            return False
        return True

    def checkCPU(self, pids):
        '''后台后的应用 CPU 占用应该小于等于 5'''
        VivoTools.LOGD("performance", "checkCPU ...")
        report = True
        cpus = {}

        def _check(cpus):
            for key in cpus:
                cpu = cpus[key]
                if cpu != "none" and int(cpu) > 5:
                    return True
            return False

        # 先sleep 3秒
        time.sleep(3)
        count = 3
        while count > 0:
            cpus = self.adb.get_cpus(pids)
            VivoTools.LOGD("performance", "cpus " + str(cpu)
            if not _check(cpus):
                report = False
            break
            time.sleep(3)
            count = count - 1

        if report:
            VivoTools.LOGD("performance", u"应用后台 CPU 异常")
            VivoTools.LOGD("performance", cpus)
            VivoReport.BugReport(u"应用后台 CPU 异常", "cpu", str(cpus), self.getApkPath(),
                                 module=self.desired_caps['appPackage'])
            return False
        return True

    def test_common(self):
        VivoTools.disableRetry()
        try:
            VivoTools.SetAppInfo(self.appInfo)
            VivoReport.SetAppInfo(self.appInfo['name'], \
                                  str(self.appInfo['versionCode']), \
                                  self.appInfo['applicationLabel'], \
                                  self.appInfo['versionName'], \
                                  0 if self.desired_caps['appActivity'] == None else 1)
            pids = {}
            if VivoTools.isAppInstalled(self.desired_caps['appPackage']) \
                    and self.desired_caps['appActivity'] != None:
                # home 后台应用
                VivoReport.Todo(u"HOME 后台应用测试")
                VivoTools.startActivity(self.desired_caps['appPackage'], \
                                        self.desired_caps['appActivity'])
                # 点击系统权限弹窗
                count = 5
                while count > 0:
                    time.sleep(1)
                    self.driver.mDevice.watchers.run()
                    count = count - 1
                time.sleep(5)
                pids = self.adb.get_pids(self.desired_caps['appPackage'])
                start_adjs = self.adb.get_adjs(pids)
                if self.homeQuit(self.desired_caps['appPackage']):
                    home_adjs = self.adb.get_adjs(pids)
                    result_adj = self.checkHomeAdj(home_adjs)
                    result_cpu = self.checkCPU(pids)
                    VivoTools.LOGD("performance", "result_adj = " + result_adj + ", result_cpu = " + result_cpu)
                    VivoTools.assertv(not (result_adj and result_cpu), 'performance')
                    VivoReport.Passed()
                    # if result_adj and result_cpu:
                    #  VivoReport.Passed()
                    # 杀掉应用所有进程
                    # self.adb.stop_app(self.desired_caps['appPackage'])
                    # back 后台应用
                    # VivoReport.Todo(u"BACK 后台应用测试")
                    # VivoTools.startActivity(self.desired_caps['appPackage'],\
                    #     self.desired_caps['appActivity'])
                    # time.sleep(5)
                    # pids = self.adb.get_pids(self.desired_caps['appPackage'])
                    # start_adjs = self.adb.get_adjs(pids)
                    # if self.backQuit(self.desired_caps['appPackage']):
                    #  back_adjs = self.adb.get_adjs(pids)
                    #  result_adj = self.checkBackAdj(back_adjs)
                    #  result_cpu = self.checkCPU(pids)
                    #  if result_adj and result_cpu:
                    #    VivoReport.Passed()
        except Exception as e:
            VivoTools.LOGE("performance", e)
            VivoTools.LOGE("performance", pids)
