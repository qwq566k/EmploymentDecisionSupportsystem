import datetime

from pydantic import BaseModel


class ZhiLianModel(BaseModel):
    cardCustomJson: str = ""
    cityDistrict: str = ""
    cityId: str = ""
    commercialLabel: list = []
    companyId: int
    companyLogo: str = ""
    companyName: str = ""
    companyNumber: str = ""
    companyRootId: int
    companyScaleTypeTagsNew: list = []
    companySize: str = ""
    companyUrl: str = ""
    education: str = ""
    featureServer: dict = {}
    financingStage: dict = {}
    firstPublishTime: datetime.datetime
    industryCompanyTags: list = []
    industryName: str = ""
    innerBusinessInfo: dict = {}
    jobId: int
    jobKnowledgeWelfareFeatures: list = []
    jobPostingTime: int
    jobRootOrgInfo: dict = {}
    jobSkillTags: list = []
    jobSummary: str = ""
    name: str = ""
    number: str = ""
    orgBestEmployerFlag: int = 0
    orgPayedFlag: int = 0
    positionCommercialLabel: list = []
    positionURL: str = ""
    property: str = ""
    propertyCode: int = 0
    publishTime: datetime.datetime
    recruitNumber: int = 1
    rootCompanyNumber: str = ""
    salary60: str = ""
    salaryReal: str = ""
    skillLabel: list = []
    staffCard: dict = {}
    streetId: int = 0
    streetName: str = ""
    subways: list = []
    welfareTagList: list = []
    workCity: str = ""
    uuid: str = ""

class BossZhipinModel(BaseModel):
    securityId:str = ""
    encryptBossId:str = ""
    bossName:str = ""
    bossTitle:str = ""
    encryptJobId:str = ""
    jobName:str = ""
    salaryDesc:str = ""
    skills:list = []
    jobExperience:str = ""
    daysPerWeekDesc:str = ""
    leastMonthDesc:str = ""
    jobDegree:str = ""
    cityName:str = ""
    areaDistrict:str = ""
    businessDistrict:str = ""
    jobType:int = 0
    city:int = 0
    gps:dict = {}
    encryptBrandId:str = ""
    brandName:str = ""
    brandStageName:str = ""
    brandIndustry:str = ""
    brandScaleName:str = ""
    welfareList:list = []
    industry:int = 0
    postDescription:str = ""
    experienceName:str = ""
    degreeName:str = ""
    address:str = ""
    encryptUserId:str = ""