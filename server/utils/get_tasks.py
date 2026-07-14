
import json
import random
from contextlib import asynccontextmanager
from typing import Dict, List, Union

import config
from model.db_model import Tasks
from model.result_model import ResponseModel
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

zhilian_tasks = json.load(
    open("task_data/zhilian.json", "r", encoding="utf-8"))
bosszhi_tasks = json.load(
    open("task_data/bosszhipin.json", "r", encoding="utf-8"))


async def get_zhilian_tasks(db: AsyncSession, token):  # 获取智联招聘任务
    city_list = zhilian_tasks["city_list"]
    if config.ONLY_HOT_CITY:
        city_list = [{"city": city, "code": zhilian_tasks["city_list"][city]} for city in zhilian_tasks["city_list"]
                     if city in config.HOT_CITY]
    city_info = random.choices(city_list)  # 随机选择一个城市
    city, code = city_info[0]["city"], city_info[0]["code"]  # 城市名称

    job_list = zhilian_tasks["job_list"]
    category = random.randint(0, len(job_list)-1)  # 随机选择一个职位类别
    job = random.randint(0, len(job_list[category]["items"])-1)  # 随机选择一个职位
    name = job_list[category]["items"][job]["name"]  # 职位名称
    kw = job_list[category]["items"][job]["kw"]  # 职位关键词
    params = json.dumps({
        "city": city,
        "category": category,
        "cityCode": code,
        "job": name,
        "kw": kw,
        "maxPage": config.ZHILIAN_MAX_PAGES
    })  # 城市名 职位类别 职位名称
    task = await db.execute(insert(Tasks).values(id=None, create_date=func.now(), params=params, platform=1, device_id=token["device_id"], success_count=0, status=0))
    await db.commit()
    return ResponseModel(data={"id": task.lastrowid, "params": json.loads(params),"platform":1})


async def get_bosszhipin_tasks(db: AsyncSession, token):  # 获取
    if config.ONLY_HOT_CITY:  # boss直聘的热门城市列表已经清洗好了
        city_list: dict = bosszhi_tasks["hot_city_list"]
    else:
        city_list: dict = bosszhi_tasks["city_list"]
    city_name: Dict[str, Dict[Union[str, int]]] = random.choices(list(city_list.keys()))[0]
    province_code, city_code = city_list[city_name]["code"], city_list[city_name]["cityCode"]  # 城市代号

    job_list = bosszhi_tasks["job_list"]
    category = random.randint(0, len(job_list)-1)  # 随机选择一个职位类别
    job = random.randint(0, len(job_list[category]["items"])-1)  # 随机选择一个职位
    name = job_list[category]["items"][job]["name"]  # 职位名称
    code = job_list[category]["items"][job]["code"]  # 职位代号

    params = json.dumps({
        "provinceCode":province_code,
        "cityCode": city_code,
        "category": category,
        "jobCode": code,
        "cityCode": city_code,
        "job": name,
        "maxPage": config.BOSSZHIPIN_MAX_PAGES
    })
    task = await db.execute(insert(Tasks).values(id=None, create_date=func.now(), params=params, platform=2, device_id=token["device_id"], success_count=0, status=0))
    await db.commit()
    return ResponseModel(data={"id": task.lastrowid, "params": json.loads(params),"platform":2})
