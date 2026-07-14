import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_parquet("data/jobinfo.parquet")
# 筛选 source_table 为 zhi_lian
data = data[data["source_table"] == "zhi_lian"]
print("数据量:",len(data),"\n")
print("城市分布:", data["city"].value_counts()[:10],"\n")
print("职位类型分布:", data["industry"].value_counts()[:10])