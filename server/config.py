# 生产环境数据库请通过环境变量或私密配置注入，勿把真实密码提交到仓库
MYSQL_URL_ASYNC = "mysql+aiomysql://127.0.0.1:3306/test?charset=utf8mb4&user=root&password=123456"  # 本地测试用

POOL_SIZE = 10
POOL_RECYCLE = 3600
POOL_TIMEOUT = 15
MAX_OVERFLOW = 10
CONNECT_TIMEOUT = 60

HOT_CITY = ["北京", "上海", "广州", "深圳", "杭州", "成都", "武汉", "重庆", "西安", "南京", "东莞", "大连",
            "沈阳", "苏州", "昆明", "长沙", "合肥", "宁波", "郑州", "天津", "青岛", "济南", "哈尔滨", "长春", "福州"]
ONLY_HOT_CITY = True  # 只爬取热门城市

TASK_VALID = 60 * 60 * 3  # 任务有效时间 3小时 若下发的任务超过有效期未完成则回收
JWT_SECRET = "lowcode"  # JWT密钥，生产环境请更换
ZHILIAN_MAX_PAGES = 20  # 每次爬取最大页数 单次20页 每批最多400条数据
BOSSZHIPIN_MAX_PAGES = 1  # 每次爬取最大页数 单次30页 每批最多300条数据

DEVICE_WHITELIST = ["*"]  # 设备白名单 *表示所有设备

CLIENT_VERSION = {"Zhilian": "1.1", "BossZhipin": "1.0"}

NOTICE = {  # 服务器公告
    "global": "全服公告测试",
    "Zhilian": "智联爬虫公告测试",
    "BossZhipin": "Boss直聘爬虫公告测试",
}