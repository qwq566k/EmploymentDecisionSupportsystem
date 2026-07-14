from playwright.sync_api import sync_playwright, Route
import json
import random


data = []

with sync_playwright() as p:
    tmp_data = []
    
    def intercept_response(route: Route):
        response = route.fetch()
        print(response.url)
        if "/wapi/zpgeek/search/joblist.json" in response.url:
            resp = response.json()
            if resp["code"] == 0:
                data.append(resp["zpData"]["jobList"])
            else:
                print(f"错误码：{resp['code']}, 错误信息：{resp['message']}")
        route.continue_()

    brower = p.chromium.launch_persistent_context(
        user_data_dir="C:\\Users\\Administrator\\AppData\\Local\\Microsoft\\Edge\\User Data", accept_downloads=True, channel="msedge", headless=False)
    brower.route(
        'https://www.zhipin.com/wapi/zpgeek/search/joblist.json?*', intercept_response)

    joblist_page = brower.pages[0]  # 获取职位列表的页面
    company_page = brower.new_page()  # 获取公司信息的页面

    # 获取用户是否登录，劝告用户退出登录，避免因本次爬虫任务影响用户后续账号使用
    userinfo = joblist_page.request.get(
        "https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json").json()
    if userinfo["code"] != 7:
        input(
            "\033[0;33;40m [WARNING] 检测到您处于登录状态，为了避免因本次爬虫任务影响您的后续账号使用，建议您先手动退出登录。待您完成操作后，在本终端按任意键继续... \033[0m")
    for i in range(1, 2):
        joblist_page.goto(
            f"https://www.zhipin.com/web/geek/job?query=python&city=101280100&position=100109&page={i}")
        joblist_page.wait_for_load_state("networkidle")
        joblist_page.wait_for_timeout(random.randint(3000, 7000))


    joblist_page.close()

json.dump(data, open("bosszhiping.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=4)
