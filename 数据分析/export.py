import pandas as pd
import xlsxwriter
import os

if os.path.exists('data/jobinfo.xlsx'):
    os.remove('data/jobinfo.xlsx')

data = pd.read_parquet('data/jobinfo.parquet')
# print(data["source_table"].unique())
data = data[~data["source_table"].isin(["xk_bosszhipin", "xk_zhongguo2", "xk_zhongguo", "xk_lago"])]
data = data.replace('\t',' ', regex=True).replace('\n',' ', regex=True)
data.to_excel('data/jobinfo.xlsx', index=False,engine='xlsxwriter')