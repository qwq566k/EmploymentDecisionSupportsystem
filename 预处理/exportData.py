"""
 需求
执行以下SQL语句，将结果迁移至另一个数据库中
SELECT *
FROM zhi_lian
WHERE workCity IN ("广州","佛山","肇庆","深圳","东莞","惠州","珠海","中山","江门")
"""



# 请填写本地或内网数据库连接，勿提交真实密码
old_url = "mysql://127.0.0.1:3306/jobinfo?charset=utf8mb4&user=root&password=YOUR_PASSWORD"
new_url = "mysql://127.0.0.1:3306/jobinfo_prd?charset=utf8mb4&user=root&password=YOUR_PASSWORD"

import asyncio
from sqlalchemy import create_engine
import pandas as pd

# >>> from sqlalchemy import create_engine  # doctest: +SKIP
# >>> engine = create_engine("sqlite:///database.db")  # doctest: +SKIP
# >>> with engine.connect() as conn, conn.begin():  # doctest: +SKIP
# ...     data = pd.read_sql_table("data", conn)  # doctest: +SKIP

engine_old = create_engine(old_url)
engine_new = create_engine(new_url)
with engine_old.connect() as conn, conn.begin():
    data = pd.read_sql_query("SELECT * FROM boss_zhipin WHERE cityName IN ('广州','佛山','肇庆','深圳','东莞','惠州','珠海','中山','江门')",conn)
with engine_new.connect() as conn, conn.begin():
    data.to_sql("boss_zhipin", conn, if_exists="append", index=False)

