from sqlalchemy import JSON, TEXT, String, DateTime,Integer
from sqlalchemy.ext.asyncio import (AsyncAttrs)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import datetime


class Base(AsyncAttrs, DeclarativeBase):
    pass


class ZhiLian(Base):  # 智联招聘结果表
    __tablename__ = "zhi_lian"
    id: Mapped[int] = mapped_column(primary_key=True)  # 数据ID
    cityDistrict: Mapped[str] = mapped_column(String(16))  # 区县
    commercialLabel: Mapped[list] = mapped_column(JSON)  # 商业标签
    companyName: Mapped[str] = mapped_column(String(64))  # 公司名称
    companyScaleTypeTagsNew: Mapped[list] = mapped_column(JSON)  # 公司规模标签
    companySize: Mapped[str] = mapped_column(String(16))  # 公司员工规模
    education: Mapped[str] = mapped_column(String(16))  # 学历要求
    industryName: Mapped[str] = mapped_column(String(16))  # 行业名称
    innerBusinessInfo: Mapped[dict] = mapped_column(JSON)  # 内部业务信息
    jobSkillTags: Mapped[list] = mapped_column(JSON)  # 职位技能标签
    jobSummary: Mapped[str] = mapped_column(TEXT(2048))  # 职位简介
    name: Mapped[str] = mapped_column(String(64))  # 职位名称
    property: Mapped[str] = mapped_column(String(16))  # 公司性质 如：民营、合资、国企、上市
    recruitNumber: Mapped[int] = mapped_column(default=1)  # 招聘人数
    salaryReal: Mapped[str] = mapped_column(String(32))  # 薪资范围
    streetName: Mapped[str] = mapped_column(String(64))  # 街道名称
    subways: Mapped[list] = mapped_column(JSON)  # 地铁信息
    workCity: Mapped[str] = mapped_column(String(16))  # 工作城市


class BossZhipin(Base):  # Boss直聘结果表
    __tablename__ = 'boss_zhipin'
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键
    jobName: Mapped[str] = mapped_column(String(128))  # 职位名称
    salaryDesc: Mapped[str] = mapped_column(String(32))  # 薪资范围
    skills: Mapped[list] = mapped_column(JSON)  # 技能要求
    jobExperience: Mapped[str] = mapped_column(String(16), default="")  # 工作经验
    daysPerWeekDesc: Mapped[str] = mapped_column(String(16), default="")  # 每周工作天数
    leastMonthDesc: Mapped[str] = mapped_column(String(16), default="")  # 最少工作月数
    degreeName: Mapped[str] = mapped_column(String(16))  # 学历要求
    cityName: Mapped[str] = mapped_column(String(32))  # 工作城市
    areaDistrict: Mapped[str] = mapped_column(String(32))  # 工作街区
    businessDistrict: Mapped[str] = mapped_column(String(32))  # 商业街区
    brandName: Mapped[str] = mapped_column(String(64))  # 公司名称
    brandStageName: Mapped[str] = mapped_column(String(32))  # 公司阶段
    brandIndustry: Mapped[str] = mapped_column(String(32))  # 公司行业
    brandScaleName: Mapped[str] = mapped_column(String(32))  # 公司规模
    postDescription: Mapped[str] = mapped_column(TEXT(5120))  # 职位描述
    experienceName: Mapped[str] = mapped_column(String(32))  # 工作经验要求
    address: Mapped[str] = mapped_column(String(256))  # 公司地址


class ZhongGuo(Base):  # 中国招聘网结果表
    __tablename__ = "zhong_guo"
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键ID
    url: Mapped[str] = mapped_column(String(100))  # 职位链接
    job: Mapped[str] = mapped_column(String(50))  # 职位名称
    salary: Mapped[str] = mapped_column(String(20))  # 工资
    company: Mapped[str] = mapped_column(String(50))  # 公司名称
    job_info: Mapped[str] = mapped_column(TEXT(1024))  # 岗位信息及要求


class XKLago(Base):  # xk 拉勾网结果表
    __tablename__ = 'xk_lago'
    id: Mapped[int] = mapped_column(primary_key=True)
    category: Mapped[str] = mapped_column(String(255))  # 职位类别(小类)
    bigcategory: Mapped[str] = mapped_column(String(255))  # 职位类别(大类)
    positionName: Mapped[str] = mapped_column(String(255))  # 职位名称
    companyFullName: Mapped[str] = mapped_column(String(255))  # 公司全称
    companySize: Mapped[str] = mapped_column(String(255))  # 公司规模
    industryField: Mapped[str] = mapped_column(String(255))  # 公司行业
    financeStage:Mapped[str]=mapped_column(String(255))  # 公司阶段
    positionType: Mapped[str] = mapped_column(String(255))  # 职位类型
    city: Mapped[str] = mapped_column(String(255))  # 工作城市
    district: Mapped[str] = mapped_column(String(255))  # 工作区县
    salary: Mapped[str] = mapped_column(String(255))  # 薪资范围
    workYear: Mapped[str] = mapped_column(String(255))  # 工作经验
    jobNature: Mapped[str] = mapped_column(String(255))  # 工作性质
    education: Mapped[str] = mapped_column(String(255))  # 学历要求
    positionDetail: Mapped[str] = mapped_column(TEXT(1024))  # 职位详情


class XKZhongGuo1(Base):  # xk 中国招聘网结果表
    __tablename__ = 'xk_zhongguo'
    id: Mapped[int] = mapped_column(primary_key=True)
    company_name: Mapped[str] = mapped_column(String(255))  # 公司名称
    position_name: Mapped[str] = mapped_column(String(255))  # 职位名称
    work_location: Mapped[str] = mapped_column(String(255))  # 工作地点
    salary_level: Mapped[str] = mapped_column(String(255))  # 薪资范围
    education_requirement: Mapped[str] = mapped_column(String(255))  # 学历要求
    company_type: Mapped[str] = mapped_column(String(255))  # 公司类型
    company_size: Mapped[str] = mapped_column(String(255))  # 公司规模
    industry: Mapped[str] = mapped_column(String(255))  # 公司行业
    job_description: Mapped[str] = mapped_column(TEXT(1024))  # 职位描述


class XKZhongGuo2(Base):  # xk 中国招聘网结果表
    __tablename__ = 'xk_zhongguo2'
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键ID
    position_name: Mapped[str] = mapped_column(String(255))  # 职位名称
    company_name: Mapped[str] = mapped_column(String(255))  # 公司名称
    company_size:Mapped[str] = mapped_column(String(255))  # 公司规模
    work_location: Mapped[str] = mapped_column(String(255))  # 工作地点
    salary_level: Mapped[str] = mapped_column(String(255))  # 薪资范围
    json: Mapped[str] = mapped_column(TEXT(1024))  # json原始数据
    property: Mapped[str] = mapped_column(TEXT(1024))  # 公司类型（国企/民企等）
    type: Mapped[str] = mapped_column(String(255))  # 公司所属行业
    job_description: Mapped[str] = mapped_column(TEXT(1024))  # 职位描述


class XKBosszhipin(Base):  # xk boss直聘结果表
    __tablename__ = 'xk_bosszhipin'
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键ID
    company: Mapped[str] = mapped_column(String(100))  # 公司名称
    name: Mapped[str] = mapped_column(String(100))  # 职位名称
    location: Mapped[str] = mapped_column(String(100))  # 工作地点
    salary: Mapped[str] = mapped_column(String(100))  # 薪资范围
    edu: Mapped[str] = mapped_column(String(500))  # 学历要求
    experience: Mapped[str] = mapped_column(TEXT(1024))  # 工作经验
    skills: Mapped[str] = mapped_column(TEXT(1024))  # 技能要求
    demand: Mapped[str] = mapped_column(TEXT(1024))  # 职位要求


class DBMerge(Base):# 数据合并表
    __tablename__ = "db_merge"
    id: Mapped[int] = mapped_column(primary_key=True)  # 主键ID
    origin_id: Mapped[int] = mapped_column(Integer)  # 原始ID
    source_table: Mapped[str] = mapped_column(String(255))  # 来源表

    industry: Mapped[str] = mapped_column(String(255),nullable=True)  # 标准化行业
    position: Mapped[str] = mapped_column(String(255),nullable=True)  # 标准化职位名称
    skills: Mapped[str] = mapped_column(TEXT(1024),nullable=True)  # 标准化技能要求(考虑存储类型不同)

    company_name: Mapped[str] = mapped_column(String(255),nullable=True)  # 公司名称
    company_scale: Mapped[str] = mapped_column(String(255),nullable=True)  # 公司规模
    company_property: Mapped[str] = mapped_column(TEXT(1024),nullable=True)  # 公司性质

    salary: Mapped[str] = mapped_column(String(255),nullable=True)  # 薪资范围
    education: Mapped[str] = mapped_column(String(255),nullable=True)  # 学历要求
    experience: Mapped[str] = mapped_column(TEXT(1024),nullable=True)  # 工作经验
    job_description: Mapped[str] = mapped_column(TEXT(1024),nullable=True)  # 职位描述
    # province:Mapped[str] = mapped_column(String(255),nullable=True)  # 工作省份
    city: Mapped[str] = mapped_column(String(255),nullable=True)  # 工作地点
    district: Mapped[str] = mapped_column(String(255),nullable=True)  # 工作区县
    street: Mapped[str] = mapped_column(String(255),nullable=True)  # 工作街道
    address: Mapped[str] = mapped_column(TEXT(1024),nullable=True)  # 详细地址
