# 根据 db_model 内列举的所有表结构，将表下所有数据合并到 db_merge 中
# 从main函数中取出
import asyncio
import json
from typing import List, Union

from sqlalchemy import func, insert, select

import db
from db_model import *


class UnitData():
    def _format_size(self, size: str):
        if not size:
            return size
        try:
            if "人以下" in size or "<" in size:
                return "0|"+size.replace("人以下", "").replace("<", "")
            elif "人以上" in size or ">" in size:
                return size.replace("人以上", "").replace(">", "")+"|99999"
            elif "少于" in size:
                return "0|"+size.replace("少于", "").replace("人", "")
            elif "人" in size:
                return size.replace("人", "").replace("-", "|")
        except Exception as e:
            print(e)
            return size.replace("-", "|")

    def _format_salary(self, salary: str):
        if not salary or salary == "":
            return "0|0"
        try:
            if not salary or salary == "":
                return "0|0"
            salary = salary.lower()
            if "·" in salary:
                salary = salary.split("·")[0]
            if "k" in salary:
                salary = salary.replace("k", "千/月")
            if "万/月" in salary:
                salary = salary.replace("万/月", "").split("-")
                # 真恶心啊
                salary = str(int(float(salary[0])*10000)) + \
                    "|"+str(int(float(salary[1])*10000))
                return salary
            if "千/月" in salary:  # 包含小数 谁设计的构思网站
                salary = salary.replace("千/月", "").split("-")
                salary = str(int(float(salary[0])*1000)) + \
                    "|"+str(int(float(salary[1])*1000))
                return salary
        except Exception as e:
            print(e)
            return salary

    async def xk_bosszhipin(self, datas: List[XKBosszhipin]):
        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="xk_bosszhipin",  # 原始表名称

                industry=None,  # 行业名称
                position=data.name if data.name else None,  # 职位名称
                skills="|".join(data.skills.split(
                    " ")) if data.skills else None,  # 技能标签

                company_name=data.company if data.company else None,  # 公司名称
                company_scale=None,  # 公司规模
                company_property=None,  # 公司类型
                salary=self._format_salary(
                    data.salary) if data.salary else None,  # 薪资
                education=data.edu if data.edu else None,  # 学历
                job_description=data.demand if data.demand else None,  # 职位描述
                city=data.location if data.location else None,  # 工作城市
                district=None,  # 工作镇街
                street=None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def xk_zhongguo2(self, datas: List[XKZhongGuo2]):
        def format_fake_list(data: str, tostr=False):

            if data == "[]" or data == []:
                return None
            if tostr:
                return data.replace("[", "").replace("]", "").replace("'", "")
            data = data.replace("'", "\"")
            try:
                return "|".join(json.loads(data))
            except:
                return data

        def format_description(content: str):
            if content == "[]":
                return None
            # 尝试移除\xa0
            content = content.strip().replace(u'\u3000', u' ').replace(u'\xa0', u' ')
            content = content.replace("['", "").replace(
                "']", "").replace("','", "\n").replace("'", "").replace(", ", "")
            return content

        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="xk_zhongguo2",  # 原始表名称

                industry=format_fake_list(
                    data.type) if data.type else None,  # 行业名称
                position=data.position_name if data.position_name else None,  # 职位名称
                skills=None,  # 技能标签

                company_name=data.company_name,  # 公司名称
                company_scale=self._format_size(
                    # 公司规模
                    format_fake_list(data.company_size)) if data.company_size else None,
                company_property=format_fake_list(
                    data.property, tostr=True) if data.property else None,  # 公司类型
                salary=self._format_salary(
                    data.salary_level) if data.salary_level else None,  # 薪资
                education=None,  # 学历
                job_description=format_description(
                    data.job_description) if data.job_description else None,  # 职位描述
                city=data.work_location.split(
                    "-")[0] if data.work_location else None,  # 工作城市
                district=data.work_location.split(
                    # 工作镇街
                    "-")[1] if len(data.work_location.split("-")) > 1 else None,
                street=None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def xk_zhongguo(self, datas: List[XKZhongGuo1]):
        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="xk_zhongguo",  # 原始表名称

                industry=data.industry if data.industry else None,  # 行业名称
                position=data.position_name if data.position_name else None,  # 职位名称
                skills=None,  # 技能标签

                company_name=data.company_name if data.company_name else None,  # 公司名称
                company_scale=self._format_size(
                    data.company_size) if data.company_size else None,  # 公司规模
                company_property=data.company_type if data.company_type else None,  # 公司类型
                salary=data.salary_level.split(".")[0]+"|"+data.salary_level.split(".")[0],  # 薪资
                education=data.education_requirement if data.education_requirement else None,  # 学历
                job_description=data.job_description.replace("['", "").replace(
                    # 职位描述
                    "']", "").replace("', '", "") if data.job_description else None,
                city=data.work_location if data.work_location else None,  # 工作城市
                district=None,  # 工作镇街
                street=None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def xk_lago(self, datas: List[XKLago]):
        def remove_html_tags(text: str):
            return text.replace("<br />", "").replace("<p>", "").replace("</p>", "").replace("&quot;", "").replace("<br/>","")
        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="xk_lago",  # 原始表名称

                industry=data.industryField if data.industryField else None,  # 行业名称
                position=data.positionName if data.positionName else None,  # 职位名称
                skills=data.positionType if data.positionType else None,  # 技能标签

                company_name=data.companyFullName if data.companyFullName else None,  # 公司名称
                company_scale=self._format_size(
                    data.companySize) if data.companySize else None,  # 公司规模
                company_property=data.financeStage if data.financeStage else None,  # 公司类型

                salary=self._format_salary(
                    data.salary) if data.salary else None,  # 薪资
                education=data.education if data.education else None,  # 学历
                job_description=remove_html_tags(
                    data.positionDetail) if data.positionDetail else None,  # 职位描述
                city=data.city if data.city else None,  # 工作城市
                district=data.district if data.district else None,  # 工作镇街
                street=None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def zhong_guo(self, datas: List[ZhongGuo]):
        merge_list = []
        for data in datas:

            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="zhong_guo",  # 原始表名称

                industry=None,  # 行业名称
                position=data.job if data.job else None,  # 职位名称
                skills=None,  # 技能标签

                company_name=data.company if data.company else None,  # 公司名称
                company_scale=None,  # 公司规模
                company_property=None,  # 公司类型

                salary=data.salary.replace("元以上/月", "")+"|"+data.salary.replace("元以上/月", "") if data.salary else None,  # 薪资
                education=None,  # 学历
                experience=None,  # 工作经验
                job_description=data.job_info if data.job_info else None,  # 职位描述
                city=None,  # 工作城市
                district=None,  # 工作镇街
                street=None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def boss_zhipin(self, datas: List[BossZhipin]):
        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="boss_zhipin",  # 原始表名称

                industry=data.brandIndustry if data.brandIndustry else None,  # 行业名称
                position=data.jobName if data.jobName else None,  # 职位名称
                skills="|".join(data.skills) if data.skills else None,  # 技能标签

                company_name=data.brandName if data.brandName else None,  # 公司名称
                company_scale=self._format_size(
                    data.brandScaleName) if data.brandScaleName else None,  # 公司规模
                company_property=data.brandStageName if data.brandStageName else None,  # 公司类型

                salary=self._format_salary(
                    data.salaryDesc) if data.salaryDesc else None,  # 薪资
                education=data.degreeName if data.degreeName else None,  # 学历
                experience=data.experienceName if data.experienceName else None,  # 工作经验
                job_description=data.postDescription if data.postDescription else None,  # 职位描述
                city=data.cityName if data.cityName else None,  # 工作城市
                district=data.areaDistrict if data.areaDistrict else None,  # 工作镇街
                street=data.businessDistrict if data.businessDistrict else None,  # 工作街道
                address=data.address if data.address else None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def zhi_lian(self, datas: List[ZhiLian]):
        merge_list = []
        for data in datas:
            merge = DBMerge(
                id=None,
                origin_id=data.id,  # 原始数据ID
                source_table="zhi_lian",  # 原始表名称

                industry=data.industryName if data.industryName else None,  # 行业名称
                position=data.name if data.name else None,  # 职位名称
                skills="|".join([item["name"]
                                for item in data.jobSkillTags]) if data.jobSkillTags else None,  # 技能标签

                company_name=data.companyName if data.companyName else None,  # 公司名称
                company_scale=self._format_size(
                    data.companySize) if data.companySize else None,  # 公司规模
                company_property=data.property if data.property else None,  # 公司类型

                salary=data.salaryReal.replace("-","|") if data.salaryReal else None,  # 薪资
                education=data.education if data.education else None,  # 学历
                experience=None,  # 工作经验
                job_description=data.jobSummary if data.jobSummary else None,  # 职位描述
                city=data.workCity if data.workCity else None,  # 工作城市
                district=data.cityDistrict if data.cityDistrict else None,  # 工作镇街
                street=data.streetName if data.streetName else None,  # 工作街道
                address=None,  # 工作详细地址
            )
            if merge.industry == None and merge.position == None and merge.skills == None:
                continue
            merge_list.append(merge)
        return merge_list

    async def allocation(self, table_name: str, data):
        manager = {
            'xk_bosszhipin': self.xk_bosszhipin,
            'xk_zhongguo2': self.xk_zhongguo2,
            'xk_zhongguo': self.xk_zhongguo,
            'xk_lago': self.xk_lago,
            'zhong_guo': self.zhong_guo,
            'boss_zhipin': self.boss_zhipin,
            'zhi_lian': self.zhi_lian
        }.get(table_name)
        if manager:
            return await manager(data)
        else:
            print(f"未找到表 {table_name} 的处理函数")


async def init_tables():
    print("正在初始化数据库表...")
    async with db.async_egn.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def main():
    unit = UnitData()
    async with db.async_session() as session:
        async with session.begin():
            tables = {
                'xk_bosszhipin': XKBosszhipin,  # √
                'xk_zhongguo2': XKZhongGuo2,  # √
                'xk_zhongguo': XKZhongGuo1,  # √
                'xk_lago': XKLago,  # √
                'zhong_guo': ZhongGuo,  # √
                'boss_zhipin': BossZhipin,  # √
                'zhi_lian': ZhiLian
            }
            v: Union[XKBosszhipin, XKZhongGuo2, XKZhongGuo1,
                     XKLago, ZhongGuo, BossZhipin, ZhiLian]
            for k, v in tables.items():
                print(f"正在处理表 {k} ...")
                # 分段获取数据
                length = await session.execute(select(func.count()).select_from(v))
                length = length.scalars().first()
                # length = 2000  # 测试用
                batchCount = 1000
                for batch_num in range(0, (length // batchCount) + 2):
                    # 获取数据
                    data = await session.execute(select(v).where(v.id >= batch_num*batchCount).limit(batchCount))
                    data = data.scalars().all()
                    # 传入UnitData类中将数据统一化为db_merge表结构
                    print(f"正在处理表 {k} 第 {batch_num + 1} 批次..")
                    data = await unit.allocation(k, data)
                    # 将数据插入到db_merge表中
                    session.add_all(data)
            print("正在保存数据...")
            await session.flush()
    print("数据合并完成！")
    await db.async_egn.dispose()

if __name__ == '__main__':
    # asyncio.run(init_tables()) # 如果不存在db_merge表，请先运行此行代码
    asyncio.run(main())
