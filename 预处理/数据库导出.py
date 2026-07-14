import asyncio

import pandas as pd
from sqlalchemy import func, select

import db
from db_model import *

batchCount = 1000


async def main():
    merge_data = []
    async with db.async_session() as session:
        async with session.begin():
            length = await session.execute(select(func.count(DBMerge.id)))
            length = length.scalars().first()
            for batch_num in range(0, (length // batchCount) + 2):
                print(f"\r\033[K{batch_num * batchCount}/{length} {batch_num *
                      batchCount / length * 100:.2f}% ", end="", flush=True)
                data = await session.execute(select(DBMerge).offset(batch_num * batchCount).limit(batchCount))
                data = data.scalars().all()
                tmp = [{
                    "id": item.id,
                    "origin_id": item.origin_id,
                    "source_table": item.source_table,
                    "industry": item.industry,
                    "position": item.position,
                    "skills": item.skills,
                    "company_name": item.company_name,
                    "company_scale": item.company_scale,
                    "company_property": item.company_property,
                    "salary": item.salary,
                    "education": item.education,
                    "experience": item.experience,
                    "job_description": item.job_description,
                    "city": item.city,
                    "district": item.district,
                    "street": item.street,
                    "address": item.address,
                } for item in data]
                merge_data.extend(tmp)
    df = pd.DataFrame(merge_data)
    print("\n移除异常字符..")
    df.replace(to_replace='\\xa0', value='', regex=True, inplace=True)
    print("储存为 merge_data.csv 文件..")
    df.to_csv("merge_data.csv", index=False)
    print("导出完成")
    await db.async_egn.dispose()

if __name__ == '__main__':
    asyncio.run(main())
