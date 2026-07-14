import datetime
import json
import random
from contextlib import asynccontextmanager

import config
import uvicorn
from aiocache import cached
from db import async_egn, db_session
from fastapi import Depends, FastAPI, Header
from model.db_model import Base, Tasks, ZhiLianResult, BossZhipinResult
from model.result_model import ResponseModel, UpdateTaskModel
from router.bosszhipin_router import router as bosszhipin_router
from router.zhilian_router import router as zhilian_router
from sqlalchemy import func, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.get_tasks import get_bosszhipin_tasks, get_zhilian_tasks
from utils.pyjwt import JWT

# 本服务用于分发爬虫任务，并接收爬虫任务结果存入数据库中。另外可查询数据状态等。
# TODO: 爬虫客户端计划多端合一，通过下发对应的模块来控制爬虫行为（即加载器+爬虫模块的方式），方便热更新。24/11/28


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_egn.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # ⚠️⚠️⚠️ 生产环境需删除 ⚠️⚠️⚠️
        await conn.run_sync(Base.metadata.create_all)
    yield
    await async_egn.dispose()


app = FastAPI(lifespan=lifespan)
# app = FastAPI(lifespan=lifespan,docs_url=None, redoc_url=None, openapi_url=None)
app.include_router(zhilian_router)
app.include_router(bosszhipin_router)

myJWT = JWT()


@app.get("/task")
async def get_task(platform: int = None, token=Depends(myJWT.check), db: AsyncSession = Depends(db_session)):  # 获取爬虫任务
    if isinstance(token, ResponseModel):
        return token
    # 查询是否存在超时任务
    # 如果platform不为空则查询对应平台
    sql = "SELECT * FROM tasks WHERE (status = 2 OR status = 0) AND create_date < NOW() - INTERVAL 3 HOUR" + (
        f" AND platform = {platform}" if platform is not None else "")
    timeout_task = await db.execute(text(sql))
    timeout_task = timeout_task.fetchall()
    if timeout_task:
        task = random.choice(timeout_task)
        # 回收任务
        await db.execute(text("UPDATE tasks SET status = 0 WHERE id=:id"), {"id": task[0]})
        await db.commit()
        return ResponseModel(data={"id": task[0], "params": json.loads(task[3]), "platform": task[2]})
    else:
        if platform is None:
            tasks = random.choice([get_bosszhipin_tasks, get_zhilian_tasks])
        elif platform == 1:
            tasks = get_zhilian_tasks
        elif platform == 2:
            tasks = get_bosszhipin_tasks
        return await tasks(db, token)


@app.post("/task/update")
async def post_task_update(update_data: UpdateTaskModel, token=Depends(myJWT.check),  db: AsyncSession = Depends(db_session)):  # 更新爬虫任务状态
    if isinstance(token, ResponseModel):
        return token
    await db.execute(update(Tasks).where(Tasks.id == update_data.task_id).values(status=update_data.status))
    await db.commit()
    return ResponseModel(data={"id": update_data.task_id, "status": update_data.status})


@app.get("/version")
async def check_version():
    return ResponseModel(data=config.CLIENT_VERSION)


@app.get("/status")
async def get_status(db: AsyncSession = Depends(db_session)):  # 查询爬虫统计数据
    @cached(ttl=60*5)
    async def status():
        unstart = select(func.count(Tasks.id)).where(Tasks.status == 0)
        processing = select(func.count(Tasks.id)).where(Tasks.status == 2)
        success = select(func.count(Tasks.id)).where(Tasks.status == 1)
        fail = select(func.count(Tasks.id)).where(Tasks.status == -1)

        zhilian = select(func.count(ZhiLianResult.id))
        xk_lago = text("SELECT COUNT(*) FROM xk_lago")

        bosszhipin = select(func.count(BossZhipinResult.id))
        xk_bosszhipin = text("SELECT COUNT(*) FROM xk_bosszhipin")

        zhongguo = text("SELECT COUNT(*) FROM zhong_guo")
        xk_zhongguo = text("SELECT COUNT(*) FROM xk_zhongguo")
        xk_zhongguo2 = text("SELECT COUNT(*) FROM xk_zhongguo2")

        unstart_count = (await db.execute(unstart)).scalars().first()
        processing_count = (await db.execute(processing)).scalars().first()
        success_count = (await db.execute(success)).scalars().first()
        fail_count = (await db.execute(fail)).scalars().first()

        zhilian_count = (await db.execute(zhilian)).scalars().first()

        zhongguo_count = (await db.execute(zhongguo)).scalars().first()
        xk_zhongguo_count = (await db.execute(xk_zhongguo)).scalars().first()
        xk_zhongguo2_count = (await db.execute(xk_zhongguo2)).scalars().first()

        xk_lago_count = (await db.execute(xk_lago)).scalars().first()

        bosszhipin_count = (await db.execute(bosszhipin)).scalars().first()
        xk_bosszhipin_count = (await db.execute(xk_bosszhipin)).scalars().first()

        return {"tasks": {"processing": processing_count, "success": success_count, "fail": fail_count, "unstart": unstart_count},
                "data_count": {
                    "zhilian": {
                        "count": zhilian_count,
                        "tableList": ["zhilian"],
                        "zhi_lian": zhilian_count
                    },
                    "zhongguo": {
                        "count": zhongguo_count+xk_zhongguo_count+xk_zhongguo2_count,
                        "tableList": ["xk_zhongguo", "xk_zhongguo2", "zhongguo"],
                        "xk_zhongguo": xk_zhongguo_count,
                        "xk_zhongguo2": xk_zhongguo2_count,
                        "zhongguo": zhongguo_count},
                    "bosszhipin": {
                        "count": bosszhipin_count+xk_bosszhipin_count,
                        "tableList": ["xk_boss", "boss_zhipin"],
                        "xk_bosszhipin": xk_bosszhipin_count,
                        "boss_zhipin": bosszhipin_count
                    },
                    "lago": {
                        "count": xk_lago_count,
                        "tableList": ["xk_lago"],
                        "xk_lago": xk_lago_count
                    }
        },
            "statistical_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    return ResponseModel(data=await status())


@app.get("/token")
async def get_token(device_id: str):  # 获取token 通过设备ID来获取
    if "*" in config.DEVICE_WHITELIST:
        return ResponseModel(data={"token": myJWT.create({"device_id": device_id})})
    else:
        if device_id in config.DEVICE_WHITELIST:
            return ResponseModel(data={"token": myJWT.create({"device_id": device_id})})
        else:
            return ResponseModel(code="40103", message="设备ID不在白名单中")


@app.get("/notice")
async def get_notice():
    return ResponseModel(data=config.NOTICE)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=12453)
