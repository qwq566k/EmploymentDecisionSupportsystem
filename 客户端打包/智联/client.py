import json
import os
import platform
import random
import sys
import time
import tomllib

import requests
from loguru import logger
from playwright.sync_api import Page, sync_playwright

__VERSION__ = "1.1"

# 日志配置
self_path = os.path.dirname(os.path.abspath(__file__))
logger.add(self_path+"/zhilian_log.log", rotation="10 MB", retention="7 days",
           encoding="utf-8", backtrace=True, diagnose=True)

# cookies配置
if os.path.exists("cookies.json"):
    cookies = json.load(open("cookies.json", "r", encoding="utf-8"))
    logger.info("已加载cookies")

# config文件配置
if not os.path.exists("config.toml"):
    with open("config.toml", "wb") as f:
        configs = """
max_page = 20 # 无cookies时最大页数
base_url = "http://doupoa.site:12454" # 后端地址
headless = false # 是否无头模式 例：为false时会有浏览器界面
channel = "msedge" # 浏览器类型 可选：chrome, msedge, chrome-beta, msedge-beta, msedge-dev
device_id = "" # 设备id，为空时自动生成"""
        f.write(configs.encode("utf-8"))
    logger.warning("未找到config.toml，已自动生成，请修改后重新运行")
    time.sleep(5)
    sys.exit()

config = tomllib.load(open("config.toml", "rb"))
cookies = {}

if config["device_id"] == "":
    config["device_id"] = platform.platform()+"-"+platform.node()


# 版本检查
version = requests.get(config["base_url"]+"/version").json()
if version["data"]["Zhilian"] != __VERSION__:
    logger.error(f"当前版本为 {__VERSION__} ，最新版本为 {version['data']['Zhilian']} ，请联系管理员更新")
    time.sleep(5)
    sys.exit()

# 获取服务器公告
notice = requests.get(config["base_url"]+"/notice").json()
if notice["code"] == 0:
    logger.info(f"全局公告：{notice["data"]["global"]}") if notice["data"]["global"] else ""
    logger.info(f"本服务公告：{notice["data"]["Zhilian"]}") if notice["data"]["Zhilian"] else ""


class TaskManager():
    token_retry = 0

    token = None

    def __init__(self):
        logger.info("正在获取token...")
        self.token = self._get_token()

    def _get_token(self):
        def retry():
            self.token_retry += 1
            return self.token_retry < 3
        try:
            data = requests.get(
                config["base_url"]+"/token", params={"device_id": config["device_id"]}).json()
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
            raise Exception(f"在执行 [ GET ] [{url}] 请求时发生异常，错误信息：{e}")

    def get_task(self):
        return self._request(config["base_url"]+"/task", params={"platform": 1})

    def update_task(self, task_id, status):
        return self._request(config["base_url"]+"/task/update", "POST", json={"task_id": task_id, "status": status})

    def submit(self, task_id, result, platform=1):
        return self._request(config["base_url"]+"/zhilian/result", "POST", json={"task_id": task_id, "data": result, "platform": platform})


def main():

    logger.info("初始化程序..")
    core = sync_playwright()
    p = core.start()
    browser = p.chromium.launch(
        headless=config["headless"], channel=config["channel"])
    context = browser.new_context()
    if cookies:
        context.add_cookies(cookies)
        logger.info("载入cookies成功")
    tm = TaskManager()

    def get_result(page: Page, url: str):
        page.goto(url)
        page.wait_for_load_state("networkidle")
        result = page.evaluate(r"""() => {
                let dom = document.querySelectorAll("script");
                let regex = new RegExp("(?<=__INITIAL_STATE__\=).*$")
                for(let i=0;i<dom.length;i++){
                    if(regex.test(dom[i].textContent)){
                        return dom[i].textContent.match(regex)[0]
                    }
                }
            }""")
        try:
            data = json.loads(result)
            return data["positionList"]
        except Exception as e:
            logger.error(f"解析页面失败:{e}")
            return None

    logger.info("初始化完成")
    while True:
        logger.info("获取任务...")
        task = tm.get_task()
        success_count = 0
        failed_count = 0
        if task is None:
            logger.info("当前无任务，等待10秒后重试")
            time.sleep(10)
            continue
        # 1. 获取任务
        params = task["params"]
        logger.info(f"成功获取任务，任务ID：{task['id']}，城市：{params['city']}，职位类目：{
                    params['category']}，职位名称：{params['job']}，爬取页数：{params['maxPage']}")

        # 2. 更新任务状态
        logger.info("开始执行任务...")
        tm.update_task(task["id"], 2)

        # 3. 执行任务
        page = context.new_page()

        retry_list: dict = {}
        no_more = 0
        for i in range(1, params["maxPage"]+1 if cookies else config["max_page"]+1):
            url = f"https://www.zhaopin.com/sou/jl{
                params['cityCode']}/{params['kw']}/p{i}"
            result = get_result(page, url=url)
            if result == [] and no_more < 3:
                no_more += 1
                logger.info(f"第{i}页无数据，跳过")
                continue
            elif no_more >= 3:
                logger.info("无更多数据，结束当前任务")
                break
            if result is None:
                logger.warning(f"第{i}页获取数据失败，稍后将进行重试")
                retry_list[str(i)] = 1
            else:
                logger.info(f"第{i}页获取数据成功")
                success_count += 1
                # 4.提交任务结果
                tm.submit(task["id"], result)
                time.sleep(random.randint(2, 7))
        logger.info(f"任务队列完成，开始重试失败任务")
        while retry_list:
            for key in list(retry_list.keys()):
                if retry_list[key] > 3:
                    logger.warning(f"第{key}页重试次数超过3次，标记为失败")
                    del retry_list[key]
                else:
                    result = random.choice([True, None])
                    if result is None:
                        logger.warning(f"第{key}页重试失败，稍后将进行重试")
                        retry_list[key] += 1
                    else:
                        logger.info(f"第{key}页重试成功")
                        del retry_list[key]

        # 5. 更新任务状态

        logger.info(f"任务完成，成功：{success_count}，失败：{failed_count}")
        tm.update_task(task["id"], 1)
        page.close()


if __name__ == '__main__':
    main()
