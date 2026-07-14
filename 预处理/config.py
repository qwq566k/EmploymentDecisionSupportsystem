# 生产环境数据库请通过环境变量或私密配置注入，勿把真实密码提交到仓库
MYSQL_URL_ASYNC = "mysql+aiomysql://127.0.0.1:3306/jobinfo?charset=utf8mb4&user=root&password=123456"  # 本地测试用

POOL_SIZE = 10
POOL_RECYCLE = 3600
POOL_TIMEOUT = 15
MAX_OVERFLOW = 10
CONNECT_TIMEOUT = 60