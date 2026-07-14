from db import db_session
from fastapi import APIRouter, Depends
from model.db_model import BossZhipinResult, Tasks
from model.result_model import ResponseModel, ResultModel
from sqlalchemy import insert, update
from sqlalchemy.ext.asyncio import AsyncSession
from utils.pyjwt import JWT

router = APIRouter(prefix="/bosszhipin")
myJWT = JWT()


@router.post("/result")
async def post_result(data: ResultModel, token=Depends(myJWT.check), db: AsyncSession = Depends(db_session)):
    if isinstance(token, ResponseModel):
        return token
    if data.platform == 2:
        await db.begin()
        item:BossZhipinResult
        for item in data.data:
            await db.execute(insert(BossZhipinResult).values(  # 无法通过字典解析
                id=None,
                securityId=item.securityId,
                encryptBossId=item.encryptBossId,
                bossName=item.bossName,
                bossTitle=item.bossTitle,
                encryptJobId=item.encryptJobId,
                jobName=item.jobName,
                salaryDesc=item.salaryDesc,
                skills=item.skills,
                jobExperience=item.jobExperience,
                daysPerWeekDesc=item.daysPerWeekDesc,
                leastMonthDesc=item.leastMonthDesc,
                jobDegree=item.jobDegree,
                cityName=item.cityName,
                areaDistrict=item.areaDistrict,
                businessDistrict=item.businessDistrict,
                jobType=item.jobType,
                city=item.city,
                gps=item.gps,
                encryptBrandId=item.encryptBrandId,
                brandName=item.brandName,
                brandStageName=item.brandStageName,
                brandIndustry=item.brandIndustry,
                brandScaleName=item.brandScaleName,
                welfareList=item.welfareList,
                industry=item.industry,
                postDescription=item.postDescription,
                experienceName=item.experienceName,
                degreeName=item.degreeName,
                address=item.address,
                encryptUserId=item.encryptUserId
            ))
            await db.execute(update(Tasks).where(Tasks.id == data.task_id).values(success_count=len(data.data), status=2))
            await db.commit()
        return ResponseModel()
    else:
        return ResponseModel(code="40002", message="平台错误")
