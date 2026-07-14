import json
import os
import platform
import random
import time
import tomllib
from typing import List
import sys

import requests
from loguru import logger
from playwright.sync_api import (BrowserContext, Page, Playwright, Route,
                                 expect, sync_playwright)
from pydantic import BaseModel

__VERSION__ = "1.0"
# 日志配置
self_path = os.path.dirname(os.path.abspath(__file__))
logger.add(self_path+"/bosszhipin_log.log", rotation="10 MB", retention="7 days",
           encoding="utf-8", backtrace=True, diagnose=True)

# cookies配置
if os.path.exists("cookies.json"):
    cookies = json.load(open("cookies.json", "r", encoding="utf-8"))
    logger.info("已加载cookies")

# config文件配置
if not os.path.exists("config.toml"):
    with open("config.toml", "wb") as f:
        configs = r"""
max_page = 20 # 无cookies时最大页数
base_url = "http://doupoa.site:12454" # 后端地址
headless = false # 是否无头模式 例：为false时会有浏览器界面
channel = "msedge" # 浏览器类型 可选：chrome, msedge, chrome-beta, msedge-beta, msedge-dev
device_id = "" # 设备id，为空时自动生成
brower_user_data_dir = "C:\\Users\\Administrator\\AppData\\Local\\Microsoft\\Edge\\User Data"
"""
        f.write(configs.encode("utf-8"))
    logger.warning("未找到config.toml，已自动生成，请修改后重新运行")
    time.sleep(5)
    sys.exit()


class Config(BaseModel):
    brower_user_data_dir: str
    headless: bool
    channel: str
    base_url: str
    max_page: int
    device_id: str

# 载入配置
config = Config.model_validate(tomllib.load(open("config.toml", "rb")))
cookies = {}

# 设备ID生成
if config.device_id == "":
    config.device_id = platform.platform()+"-"+platform.node()

# 版本检查
version = requests.get(config.base_url+"/version").json()
if version["data"]["BossZhipin"] != __VERSION__:
    logger.error(f"当前版本为 {__VERSION__} ，最新版本为 {version['data']['BossZhipin']} ，请联系管理员更新")
    time.sleep(5)
    sys.exit()

# 获取服务器公告
notice = requests.get(config.base_url+"/notice").json()
if notice["code"] == 0:
    logger.info(f"全局公告：{notice["data"]["global"]}") if notice["data"]["global"] else ""
    logger.info(f"本服务公告：{notice["data"]["BossZhipin"]}") if notice["data"]["BossZhipin"] else ""


class Params(BaseModel):
    provinceCode: int
    cityCode: str
    category: int
    jobCode: int
    job: str
    maxPage: int


class Task(BaseModel):
    id: int
    params: Params
    platform: int = 2


class TaskManager():
    token_retry = 0
    token = None

    def __init__(self):
        logger.info("获取token...")
        self.token = self._get_token()

    def _get_token(self):
        def retry():
            self.token_retry += 1
            return self.token_retry < 3
        try:
            data = requests.get(
                config.base_url+"/token", params={"device_id": config.device_id}).json()
            if data["code"] == 0:
                self.token_retry = 0
                return data["data"]["token"]
            else:
                raise Exception("获取token失败")
        except Exception as e:
            if retry():
                logger.warning(f"获取token失败，正在重试第{self.token_retry}次...")
                return self._get_token()
            else:
                logger.error(f"获取token失败，错误信息：{e}")
                raise Exception("获取token失败，程序退出")

    def _request(self, url, method="GET", data={}, params={}, headers={}, json={}):
        headers["token"] = self.token
        if method == "GET":
            resp = requests.get(url, params=params, headers=headers, json=json)
        elif method == "POST":
            resp = requests.post(
                url, data=data, params=params, headers=headers, json=json)

        try:
            resp = resp.json()
            if resp["code"] == 0:
                return resp["data"]
            elif resp["code"] in [40101, 40102]:  # token过期 或 超时
                logger.warning("token过期，正在重新获取token...")
                self.token = self._get_token()
                time.sleep(2)
                return self._request(url, method, data, params, headers, json)
            else:
                logger.error(f"在执行 [ GET ] [{url}] 请求时发生异常，错误信息：{resp['msg']}")
        except Exception as e:
            logger.error(resp)
            logger.error(data)
            raise Exception(f"在执行 [ GET ] [{url}] 请求时发生异常，错误信息：{e}")


    def get_task(self):
        return self._request(config.base_url+"/task", params={"platform": 2})

    def update_task(self, task_id, status):
        return self._request(config.base_url+"/task/update", "POST", json={"task_id": task_id, "status": status})

    def submit(self, task_id, result, platform=2):
        results = []
        for item in result:
            results.append(self._request(config.base_url+"/bosszhipin/result", "POST", json={"task_id": task_id, "data": item, "platform": platform}))
        return results


class BossZhiPingCrawer():
    base_url = "https://www.zhipin.com"
    isLogin = True
    _p: Playwright = None
    _brower: BrowserContext
    _job_data: List[List[dict]] = []
    _task_data: Task = None
    _joblist_page: Page = None
    _no_more = False

    def __init__(self):
        self.p = sync_playwright().start()  # 启动浏览器
        self._brower = self.p.chromium.launch_persistent_context(
            user_data_dir=config.brower_user_data_dir, headless=config.headless, channel=config.channel, slow_mo=500)
        if cookies:
            self._brower.add_cookies(cookies)
            logger.info("已加载cookies")
        # 注入拦截器
        self._brower.route(
            'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?*', self._intercept_joblist_response)

    def _intercept_joblist_response(self, route: Route):  # 拦截器
        response = route.fetch()
        if "/wapi/zpgeek/search/joblist.json" in response.url:
            resp = response.json()
            if resp["code"] == 0:
                if len(resp["zpData"]["jobList"]) == 0 :
                    logger.info("没有更多数据了")
                    self._joblist_page.evaluate("""(function(){ document.getElementsByTagName('body')[0].id = 'all_done'})()""")
                else:
                    self._job_data.append(resp["zpData"]["jobList"])
                    index = len(self._job_data)-1
                    logger.info(f"第{index+1}批职位列表获取成功")
                    self._get_description(index)
            else:
                logger.warning(f"错误码：{resp['code']}, 错误信息：{
                               resp['message']},URL:{response.url}")
        route.continue_()

    def _get_description(self, index: int):
        logger.info(f"正在获取第{index+1}批职位详情...")

        jobs = self._job_data[index]
        for i in range(len(jobs)):
            retry = 0
            while True:
                if retry >= 3:
                    logger.error(f"获取第{index+1}批第{i}条职位详情失败，已重试3次，放弃...")
                    break
                data = self._joblist_page.request.get(f"https://www.zhipin.com/wapi/zpgeek/job/card.json?securityId={
                                                      jobs[i]['securityId']}&lid={jobs[i]['lid']}&sessionId=").json()
                if data["code"] == 0:
                    self._job_data[index][i].update(data["zpData"]["jobCard"])
                    logger.info(f"第{index+1}批第{i+1}条职位详情获取成功")
                    break
                else:
                    retry += 1
                    logger.warning(
                        f"获取第{index+1}批第{i+1}条职位详情失败，重试中... {retry}/3")
            time.sleep(random.uniform(0.5, 1.5))
        self._joblist_page.evaluate(
            """(function(){ document.getElementsByTagName('body')[0].id = 'all_done'})()""")

    def __del__(self):
        self._brower.close()
        self.p.stop()

    @property
    def task_data(self):
        return self._task_data

    @task_data.setter
    def task_data(self, value):
        self._task_data = value


    def set_task(self,task):
        self._task_data = Task.model_validate(task)
        logger.info(f"任务信息：{self._task_data.__dict__}")

    def run(self):
        if self._joblist_page is None:
            self._joblist_page = self._brower.pages[0]

        if self.isLogin:
            userinfo = self._brower.new_page()
            data = userinfo.request.get(
                "https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json").json()
            if data["code"] != 7:
                self.isLogin = True
                input(
                    "\033[0;33;40m [WARNING] 检测到您处于登录状态，为了避免因本次爬虫任务影响您的后续账号使用，建议您先手动退出登录。待您完成操作后，在本终端按任意键继续... \033[0m")
            else:
                self.isLogin = False
            userinfo.close()

        for i in range(1, self._task_data.params.maxPage+1):
            if self._no_more:
                self._no_more = False
                break
            # https://www.zhipin.com/web/geek/job?city=101280100&position=100109
            self._joblist_page.goto(f"{self.base_url}/web/geek/job?query=&city={
                                    self._task_data.params.provinceCode}&position={self._task_data.params.jobCode}&page={i}")
            # 断言等待body标签的ID变为"all_done"
            expect(self._joblist_page.locator("body"),
                   "等待任务是否完成").to_have_id("all_done", timeout=60000)
        return self._job_data


def main():
    logger.info("初始化程序")
    tm = TaskManager()
    zp = BossZhiPingCrawer()
    logger.info("初始化完成")
    while True:
        zp.task_data = None # 清空任务
        logger.info("获取任务..")
        task = tm.get_task()
        if not task:
            logger.warning("当前无任务，等待10秒后重试")
            time.sleep(10)
            continue
        else:
            zp.set_task(task) # 设置任务
            logger.info("开始执行任务...")
            tm.update_task(task["id"],2)
            data = zp.run()
            tm.submit(task["id"], data,platform=2)
            tm.update_task(task["id"], 1)
            logger.info("本次任务执行完成")

if __name__ == "__main__":
    main()