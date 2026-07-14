# 本工具将读取Mysql指定表数据写入Parquet文件中
import sqlalchemy as st
import dask.dataframe as dd
import re
import pandas as pd

print("读取数据..")
df: dd.DataFrame = dd.read_sql("db_merge", "mysql+pymysql://root:123456@localhost:3306/jobinfo", index_col="id")
print("指定字段类型..")
# df = df.astype({"address": "str", "city": "str", "company_name": "str", "company_property": "str", "company_scale": "str", "district": "str", "education": "str",
#                 "experience": "str", "job_description": "str", "origin_id": "i8", "position": "str", "salary": "str", "skills": "str", "source_table": "str", "street": "str"})

def parse_industry(dff: dd.DataFrame):
    print("解析行业..")
    replace_table = str.maketrans({"，": "|", "｜": "|", "丨": "|", ",": "|"})
    # 使用explode将分割后的列表转换为新的行
    return dff.assign(industry=dff["industry"].str.translate(replace_table).str.split("|")).explode("industry").drop_duplicates()

def process_salary(dff: dd.DataFrame):
    print("处理薪资..")

    def format_salary(df: dd.DataFrame):
        print("格式化薪资..")

        def check_salary(value):
            # 检查值是否为字符串，仅包含数字和 "|" 符号
            if isinstance(value, str) and re.match(r'^\d+(\|\d+)?$', value):
                return re.sub('[a-zA-Z]', '', value)
            else:
                return None
        # 对 "salary" 列应用检查函数
        df['salary'] = df['salary'].apply(check_salary)
        df.dropna(subset=['salary'], inplace=True)
        return df

    def parse_salary(df: dd.DataFrame):  # 解析薪资
        print("解析薪资..")
        df = df.assign(min_salary=lambda x: x["salary"].str.split("|").str[0].astype(int),
                        max_salary=lambda x: x["salary"].str.split("|").str[1].astype(int))
        df = df.assign(mid_salary=lambda x: (
            x["min_salary"] + x["max_salary"]) / 2)
        return df

    dff = format_salary(dff)
    dff = parse_salary(dff)
    return dff

print("去除空值..")
df = df.fillna("")  # 将NaN替换为pd.NA
df = df.replace(pd.NA, None)  # 将pd.NA替换为None
df = df.replace("", None)  # 将空字符串替换为None
df = df.map_partitions(lambda dff: parse_industry(dff))  # 将industry列解析为多行
df = df.map_partitions(lambda dff: process_salary(dff))  # 处理salary列并解析为多行
df = df.compute()

print("保存数据..")
df.to_parquet("jobinfo.parquet")
print(f"累计行：{len(df)}")
print("完成")
