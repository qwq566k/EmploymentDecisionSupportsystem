from sqlalchemy import JSON, TEXT, String, func, insert, select, text, update
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass


class Tasks(Base):  # 任务表
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(primary_key=True)  # 任务id
    create_date: Mapped[datetime.datetime] = mapped_column(
        default=func.now())  # 创建时间
    platform: Mapped[int]  # 平台 1:智联 2:前程
    params: Mapped[str] = mapped_column(String(1024), nullable=True)  # 所有有关于任务的参数全部存放于此，客户端根据任务类型判断
    device_id: Mapped[str] = mapped_column(String(64), nullable=True)  # 设备id
    success_count: Mapped[int] = mapped_column(default=0)  # 成功爬取信息次数
    failed_count: Mapped[int] = mapped_column(default=0)  # 爬取信息失败次数
    status: Mapped[int] = mapped_column(default=0)  # 任务状态 0:未开始 1:已完成 2:进行中 -1:失败


class ZhiLianResult(Base):  # 智联招聘结果表
    __tablename__ = "zhi_lian"
    id: Mapped[int] = mapped_column(primary_key=True)  # 数据ID
    cardCustomJson: Mapped[str] = mapped_column(
        TEXT(1024))  # 元数据 包含工作地址、公司名称、工资情况等基本信息
    cityDistrict: Mapped[str] = mapped_column(String(16))  # 区县
    cityId: Mapped[str] = mapped_column(String(16))  # 城市ID
    commercialLabel: Mapped[list] = mapped_column(JSON)  # 商业标签
    companyId: Mapped[str] = mapped_column(String(16))  # 公司ID
    companyLogo: Mapped[str] = mapped_column(TEXT(1024))  # 公司logo
    companyName: Mapped[str] = mapped_column(String(64))  # 公司名称
    companyNumber: Mapped[str] = mapped_column(String(16))  # 公司编号
    companyRootId: Mapped[int]  # 公司根ID
    companyScaleTypeTagsNew: Mapped[list] = mapped_column(JSON)  # 公司规模标签
    companySize: Mapped[str] = mapped_column(String(16))  # 公司员工规模
    companyUrl: Mapped[str] = mapped_column(TEXT(1024))  # 公司主页地址
    education: Mapped[str] = mapped_column(String(16))  # 学历要求
    featureServer: Mapped[dict] = mapped_column(JSON)  # HR回复效率
    financingStage: Mapped[dict] = mapped_column(JSON)  # 公司融资情况
    firstPublishTime: Mapped[datetime.datetime]  # 首次发布时间
    industryCompanyTags: Mapped[list] = mapped_column(JSON)  # 行业标签
    industryName: Mapped[str] = mapped_column(String(16))  # 行业名称
    innerBusinessInfo: Mapped[dict] = mapped_column(JSON)  # 内部业务信息
    jobId: Mapped[str] = mapped_column(String(16))  # 职位ID
    jobKnowledgeWelfareFeatures: Mapped[list] = mapped_column(
        JSON)  # 福利标签
    jobPostingTime: Mapped[str] = mapped_column(String(16))   # 职位发布时间 !!改!!
    jobRootOrgInfo: Mapped[dict] = mapped_column(JSON)  # 职位根组织信息
    jobSkillTags: Mapped[list] = mapped_column(JSON)  # 职位技能标签
    jobSummary: Mapped[str] = mapped_column(TEXT(2048))  # 职位简介
    name: Mapped[str] = mapped_column(String(64))  # 职位名称
    number: Mapped[str] = mapped_column(String(64))  # 职位ID
    orgBestEmployerFlag: Mapped[int] = mapped_column(default=0)  # 是否为优秀雇主
    orgPayedFlag: Mapped[int] = mapped_column(default=0)  # 是否为付费职位
    positionCommercialLabel: Mapped[list] = mapped_column(JSON)  # 职位商业标签
    positionURL: Mapped[str] = mapped_column(TEXT(1024))  # 职业详情页地址
    property: Mapped[str] = mapped_column(String(16))  # 公司性质 如：民营、合资、国企、上市
    propertyCode: Mapped[int] = mapped_column(default=0)  # 公司性质编码
    publishTime: Mapped[datetime.datetime]  # 发布时间
    recruitNumber: Mapped[int] = mapped_column(default=1)  # 招聘人数
    rootCompanyNumber: Mapped[str] = mapped_column(String(16))  # 公司根编号
    salary60: Mapped[str] = mapped_column(String(16))  # 薪资范围
    salaryReal: Mapped[str] = mapped_column(String(32))  # 薪资范围
    skillLabel: Mapped[list] = mapped_column(JSON)  # 技能标签
    staffCard: Mapped[dict] = mapped_column(JSON)  # HR信息卡片
    streetId: Mapped[int]   # 街道ID
    streetName: Mapped[str] = mapped_column(String(64))  # 街道名称
    subways: Mapped[list] = mapped_column(JSON)  # 地铁信息
    welfareTagList: Mapped[list] = mapped_column(JSON)  # 福利标签
    workCity: Mapped[str] = mapped_column(String(16))  # 工作城市
    uuid: Mapped[str] = mapped_column(String(64))  # 职位唯一标识

class BossZhipinResult(Base): # Boss直聘结果表
    __tablename__ = 'boss_zhipin'
    id: Mapped[int] = mapped_column(primary_key=True) #主键
    securityId:Mapped[str] = mapped_column(String(128)) #安全ID
    encryptBossId:Mapped[str] = mapped_column(String(64)) #加密BossID
    bossName:Mapped[str] = mapped_column(String(16)) #Boss名称
    bossTitle:Mapped[str] = mapped_column(String(32)) #Boss职位
    encryptJobId:Mapped[str] = mapped_column(String(64)) #加密职位ID
    jobName:Mapped[str] = mapped_column(String(128)) #职位名称
    salaryDesc:Mapped[str] = mapped_column(String(32)) #薪资范围
    skills:Mapped[list] = mapped_column(JSON) #技能要求
    jobExperience:Mapped[str] = mapped_column(String(16),default="") #工作经验
    daysPerWeekDesc:Mapped[str] = mapped_column(String(16),default="") #每周工作天数
    leastMonthDesc:Mapped[str] = mapped_column(String(16), default="") #最少工作月数
    jobDegree:Mapped[str] = mapped_column(String(16)) # 学历要求
    cityName:Mapped[str] = mapped_column(String(32)) # 工作城市
    areaDistrict:Mapped[str] = mapped_column(String(32)) # 工作街区
    businessDistrict:Mapped[str] = mapped_column(String(32)) # 商业街区
    jobType:Mapped[int] # 工作类型
    city:Mapped[int]
    gps:Mapped[dict] = mapped_column(JSON) # 办公地点GPS坐标
    encryptBrandId:Mapped[str] = mapped_column(String(64)) #加密公司ID
    brandName:Mapped[str] = mapped_column(String(64)) #公司名称
    brandStageName:Mapped[str] = mapped_column(String(32)) #公司阶段
    brandIndustry:Mapped[str] = mapped_column(String(32)) #公司行业
    brandScaleName:Mapped[str] = mapped_column(String(32)) #公司规模
    welfareList:Mapped[list] = mapped_column(JSON) #公司福利
    industry:Mapped[int] # 行业ID
    postDescription:Mapped[str] = mapped_column(TEXT(5120)) #职位描述
    experienceName:Mapped[str] = mapped_column(String(32)) # 工作经验要求
    degreeName:Mapped[str] = mapped_column(String(32)) # 学历要求
    address:Mapped[str] = mapped_column(String(256)) # 公司地址
    encryptUserId:Mapped[str] = mapped_column(String(64)) #加密用户ID
