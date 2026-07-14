from datetime import datetime

import pymysql
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json

# 本项目实现一个非常简单的数据标注系统，通过FastAPI框架搭建一个简单的Web服务，用于获取和提交数据标注结果。具体来说，该系统包括两个主要功能：
# 1. 获取数据：通过HTTP GET请求从数据库中随机获取一条未标注或未检查的数据，并返回其ID、文本内容、关键词、检查状态和检查时间。
# 2. 提交数据：通过HTTP POST请求提交数据标注结果，包括数据的ID和标注的关键词，并更新数据库中的对应记录。
# 该系统使用MySQL数据库存储数据，通过pymysql库连接数据库并执行SQL查询和更新操作。
# 此外，该系统还实现了数据标注结果的统计功能，通过HTTP GET请求返回数据库中已标注数据的数量。




class Response(BaseModel):
    id: int
    keywords: list


app = FastAPI()


def get_conn():
    conn = pymysql.connect(host='localhost', user='root',
                           password='123456', database='dataset')
    return conn


@app.get("/",response_class=HTMLResponse)
def index():
    html = open("index.html", "r", encoding="utf-8").read()
    return HTMLResponse(content=html, status_code=200)


@app.get("/data")
def get_once(random=False, check=False):  # 是否随机获取数据 是否返回已经被检查过的数据
    conn = get_conn()
    with conn.cursor() as cursor:
        if random: # 随机获取数据
            sql = "SELECT * FROM dataset ORDER BY RAND() LIMIT 1"
        elif check: # 展示已经被检查过的数据
            sql = "SELECT * FROM dataset ORDER BY id ASC LIMIT 1"
        elif check and random: # 随机展示已经被检查过的数据
            sql = "SELECT * FROM dataset WHERE checked = 1 ORDER BY RAND() LIMIT 1"
        else: # 按照id顺序获取数据
            sql = "SELECT * FROM dataset WHERE checked != 1 ORDER BY id ASC LIMIT 1"
        cursor.execute(sql)
        result = cursor.fetchone()
        # 替换text中第一个空格为换行符
        if result:
            return {"id": result[0], "text": result[1], "keywords": result[2], "checked": result[3], "check_time": result[4]}
        else:
            return {"message": "No data available"}


@app.post("/data")
def post_once(data: Response):
    conn = get_conn()
    with conn.cursor() as cursor:
        sql = "UPDATE dataset SET keywords = %s, checked = 1, check_time = %s WHERE id = %s"
        # try:
        cursor.execute(sql, (json.dumps(data.keywords, ensure_ascii=False), datetime.now(), str(data.id),))
        conn.commit()
        # except:
        #     conn.rollback()
        #     return {"message": "Data update failed"}
    return {"message": "Data updated successfully"}


@app.get("/status")
def get_status():
    conn = get_conn()
    with conn.cursor() as cursor:
        sql = "SELECT COUNT(*) FROM dataset WHERE checked = 1"
        cursor.execute(sql)
        checked = cursor.fetchone()
        sql = "SELECT COUNT(*) FROM dataset"
        cursor.execute(sql)
        total = cursor.fetchone()
        return {"checked": checked[0], "total": total[0]}
    return {"checked": 0}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
