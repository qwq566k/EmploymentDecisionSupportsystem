from fastapi import APIRouter,Depends
from model.result_model import ResponseModel,ResultModel
from model.db_model import ZhiLianResult,Tasks
from db import db_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert,update
from utils.pyjwt import JWT



router = APIRouter(prefix="/zhilian")
myJWT = JWT()

@router.post("/result")
async def post_result(data: ResultModel, token=Depends(myJWT.check),  db: AsyncSession = Depends(db_session)):  # 接收爬虫任务结果
    if isinstance(token, ResponseModel):
        return token
    if data.platform == 1:
        await db.begin()
        item:ZhiLianResult # 类型预注释
        for item in data.data:
            await db.execute(insert(ZhiLianResult).values(  # 无法传入dict解析
                id=None,
                cardCustomJson=item.cardCustomJson,
                cityDistrict=item.cityDistrict,
                cityId=item.cityId,
                commercialLabel=item.commercialLabel,
                companyId=item.companyId,
                companyLogo=item.companyLogo,
                companyName=item.companyName,
                companyNumber=item.companyNumber,
                companyRootId=item.companyRootId,
                companyScaleTypeTagsNew=item.companyScaleTypeTagsNew,
                companySize=item.companySize,
                companyUrl=item.companyUrl,
                education=item.education,
                featureServer=item.featureServer,
                financingStage=item.financingStage,
                firstPublishTime=item.firstPublishTime,
                industryCompanyTags=item.industryCompanyTags,
                industryName=item.industryName,
                innerBusinessInfo=item.innerBusinessInfo,
                jobId=item.jobId,
                jobKnowledgeWelfareFeatures=item.jobKnowledgeWelfareFeatures,
                jobPostingTime=item.jobPostingTime,
                jobRootOrgInfo=item.jobRootOrgInfo,
                jobSkillTags=item.jobSkillTags,
                jobSummary=item.jobSummary,
                name=item.name,
                number=item.number,
                orgBestEmployerFlag=item.orgBestEmployerFlag,
                orgPayedFlag=item.orgPayedFlag,
                positionCommercialLabel=item.positionCommercialLabel,
                positionURL=item.positionURL,
                property=item.property,
                propertyCode=item.propertyCode,
                publishTime=item.publishTime,
                recruitNumber=item.recruitNumber,
                rootCompanyNumber=item.rootCompanyNumber,
                salary60=item.salary60,
                salaryReal=item.salaryReal,
                skillLabel=item.skillLabel,
                staffCard=item.staffCard,
                streetId=item.streetId,
                streetName=item.streetName,
                subways=item.subways,
                welfareTagList=item.welfareTagList,
                workCity=item.workCity,
                uuid=item.uuid,
            ))
        await db.execute(update(Tasks).where(Tasks.id == data.task_id).values(success_count=len(data.data), status=2))
        await db.commit()
        return ResponseModel()
    else:
        return ResponseModel(code="40002", message="平台错误")

