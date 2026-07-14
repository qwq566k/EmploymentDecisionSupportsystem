import re

import dask.dataframe as dd
import jieba
import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# 步骤：
# 1. 词频分析和TF-IDF：初步筛选高频关键词。
# 2. n-gram模型：找出技能相关的短语。
# 3. 人工审查：筛选和确认与技能相关的词汇。
# 4. 优化：根据结果调整方法，如改进分词、扩展技能库等。

stopwords = [line.strip() for line in open(
    'data/stopwords.txt', 'r', encoding='utf-8').readlines()]
jieba.load_userdict('data/user_dict.txt')

print("读取数据中..")
df: dd.DataFrame = dd.read_parquet('data/jobinfo.parquet')  # 读取30万条数据
print("取出样本数据..")
df = df.sample(frac=0.001).compute()  # 取出样本数据 该数据为Pandas DataFrame类型
print("数据预处理中..")
df = df.loc[:, df.columns == "job_description"]  # 重新赋值
df = df.replace(to_replace="", value=np.nan)  # 去除空值
df = df.dropna()  # 清除空值
df = df.reset_index(drop=True)  # 重置索引
print(f"将使用{len(df)}条数据用于训练")

# 分词函数


def chinese_tokenizer(text):
    return jieba.lcut(text)


print("分词中..")
df = dd.from_pandas(df, npartitions=1)  # 将Pandas DataFrame转换为Dask DataFrame
df["job_description"] = df["job_description"].map_partitions(
    lambda dff: dff.apply(chinese_tokenizer), meta=("job_description", "object"))
# 筛选规则：去除停用词，保留长度大于1且小于10的词，去除\r\n
df["job_description"] = df["job_description"].map_partitions(
    lambda dff:
        dff.apply(
            lambda x:
                " ".join(
                    [re.sub(r'\r\n', '', word)
                     for word in x
                     if word not in stopwords and len(word) > 1 and len(word) < 10
                     ]
                )
        ), meta=("job_description", "str"))
df = df.compute()

# 词频分析
print("词频分析中..")
count_vectorizer = CountVectorizer(
    tokenizer=chinese_tokenizer, token_pattern=None)
count_matrix: csr_matrix = count_vectorizer.fit_transform(
    df["job_description"])
count_df = pd.DataFrame(count_matrix.toarray(),
                        columns=count_vectorizer.get_feature_names_out())
# 结果为单词出现次数，将每行相加后转置，再按照总数排序
# count_df = count_df.replace(to_replace=0, value=np.nan)  # 将值为0的替换为空值 但此处求相加可以忽略
count_df = count_df.drop(count_df.columns[[0]],axis=1) # 删除必为空格的列，无法正常去除
count_df = count_df.sum(axis=0).sort_values(ascending=False)


# TF-IDF分析
print("TF-IDF分析中..")
tfidf_vectorizer = TfidfVectorizer(
    tokenizer=chinese_tokenizer, token_pattern=None)
tfidf_matrix = tfidf_vectorizer.fit_transform(df["job_description"])
tfidf_df = pd.DataFrame(tfidf_matrix.toarray(),
                        columns=tfidf_vectorizer.get_feature_names_out())
# 结果为单词出现频率，将每行相加并求得平均数后转置，再按照平均数排序
tfidf_df = tfidf_df.replace(to_replace=0.0, value=np.nan)  # 将值为0.0的替换为空值
tfidf_df = tfidf_df.drop(tfidf_df.columns[[0]],axis=1) # 删除必为空格的列，无法正常去除
tfidf_df = tfidf_df.mean(axis=0).sort_values(ascending=False)


# 保存数据帧到CSV文件
print("保存数据中..")
tfidf_df.to_csv(f"output/TF-IDF分析 - 使用{len(df)}条数据.csv", mode="w+")
count_df.to_csv(f"output/词频分析 - 使用{len(df)}条数据.csv", mode="w+")
