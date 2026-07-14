# 复制为 config.py 后填写本地/服务器配置

MYSQL_URL_ASYNC = "mysql+aiomysql://127.0.0.1:3306/jobinfo?charset=utf8mb4&user=root&password=YOUR_PASSWORD"

POOL_SIZE = 10
POOL_RECYCLE = 3600
POOL_TIMEOUT = 15
MAX_OVERFLOW = 10
CONNECT_TIMEOUT = 60

HOT_CITY = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "重庆", "西安", "南京", "东莞", "大连",
            "沈阳", "苏州", "昆明", "长沙", "合肥", "宁波", "郑州", "天津", "青岛", "济南", "哈尔滨", "长春", "福州"]
ONLY_HOT_CITY = True  # 只爬取热门城市

TASK_VALID = 60 * 60 * 3  # 任务有效时间（秒），超时未完成则回收
JWT_SECRET = "change-me"  # JWT 密钥，生产环境请更换
ZHILIAN_MAX_PAGES = 20
BOSSZHIPIN_MAX_PAGES = 1

DEVICE_WHITELIST = ["*"]  # 设备白名单，* 表示全部

CLIENT_VERSION = {"Zhilian": "1.1", "BossZhipin": "1.0"}

NOTICE = {
    "global": "",
    "Zhilian": "",
    "BossZhipin": "",
}
