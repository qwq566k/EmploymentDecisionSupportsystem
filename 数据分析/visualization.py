import pandas as pd
import dask.dataframe as dd
import streamlit as st


demand = """
1. 行业分布
    - 各行业分布
        - 按城市及薪酬分布
    - 所有行业按城市分布
    - 重点行业按城市分布
        - 软件信息技术
        - 互联网相关服务
        - 大数据与AI
2. 岗位分析
    - 所有数据
        - 按薪酬及数量排序
    - 重点岗位数据
        - 按薪酬及数量排序
3. 技能关键词分析
    - 所有数据按薪资及数量排序
        - Java开发
        - Python开发
        - C++开发
    - 重点岗位数据按薪资及数量排序
        - 软件信息技术
        - 互联网相关服务
        - 大数据与AI
4. 其他关键词分析
    - 城市分布
    - 城市内区域分布
    - 公司规模
    - 公司类型
        - 民企
        - 国企
    - 薪资
    - 学历要求
    - 工作经验
"""


status = st.empty()

with status.container():
    global df
    df: dd.DataFrame

    with st.spinner("加载jobinfo.parquet数据中..."):
        df = dd.read_parquet("jobinfo.parquet").compute()
    st.success("jobinfo.parquet数据加载完成")

    # 行业分布 - 按城市
    with st.spinner("1.1 行业分布 - 按城市 -> [计算中...]"):
        df_indu_city_filter = df.drop_duplicates(
            subset=["company_name"])  # 根据公司名去重数据
        indu_city_count = df_indu_city_filter.groupby(
            ["city", "industry"]).size().unstack(fill_value=0)
        # 统计各行业各城市数量
        indu_city_count = indu_city_count.stack().reset_index()
        indu_city_count.columns = ["city", "industry", "count"]
        indu_city_count = indu_city_count[indu_city_count["industry"].notna()]
        # 筛选出数量大于0的城市
        indu_city_count = indu_city_count[indu_city_count["count"] > 0]
        indu_city_count = indu_city_count.reset_index(drop=True)  # 重置索引
        indu_city_list = indu_city_count.groupby(
            "city")["count"].sum().reset_index()  # 统计各城市数量
        indu_city_list = indu_city_list.sort_values(
            by="count", ascending=False)  # 按数量排序
        indu_city_list["name"] = indu_city_list["city"] + " - " + \
            indu_city_list["count"].astype(str) + "条"  # 添加名称列
    st.write(":material/check: 1.1 行业分布 - 按城市 -> [计算完成]")

    # 行业分布 - 按薪酬
    with st.spinner("1.2 行业分布 - 按薪酬 -> [计算中...]"):
        df_indu_salary_grouped = df.groupby("industry").agg(  # 此处按行业为组合，计算各列的统计值
            {"min_salary": "min", "mid_salary": "mean", "max_salary": "max"}).reset_index().dropna(axis=0, subset=["industry"]).astype({"min_salary": int, "mid_salary": int, "max_salary": int})
    st.write(":material/check: 1.2 行业分布 - 按薪酬 -> [计算完成]")

status.empty()


def main():
    st.write("# 职位数据分析")
    st.write("## 1. 需求分析")
    with st.expander("展开"):
        st.write(demand)
    st.write("## 2. 数据分析")
    st.write("### 2.1 行业分布")

    with st.expander("2.1.1 按城市分布"):
        # 按城市筛选，并按行业分组，筛选出行业不为空的城市。筛选后按数量排序
        st.write("_注：本数据先按城市分大类，随后按“行业”列聚合排序，已按公司名为基准进行去重_")
        # 对city去重
        indu_city_selected = st.selectbox(
            "此处选择城市", indu_city_list["name"].tolist())
        if indu_city_selected:
            indu_city_selected = indu_city_selected.split(" - ")[0]
            st.write(f"#### {indu_city_selected} 各行业分布")
            indu_city_selected = indu_city_count[indu_city_count["city"].str.contains(
                indu_city_selected)]  # 筛选相关城市
            indu_city_selected = indu_city_selected.sort_values(
                by="count", ascending=False)  # 按数量排序
            indu_city_selected = indu_city_selected.reset_index()  # 重置索引
            st.dataframe(indu_city_selected.drop(
                ["index", "city"], axis=1), use_container_width=True, hide_index=True, column_config={"industry": "行业", "count": "数量"})
        else:
            st.write("请选择城市")

    with st.expander("2.1.2 按薪酬分布"):
        indu_salary_selected = st.selectbox(
            "此处选择筛选条件", ["按最低薪酬排序", "按平均薪酬排序", "按最高薪酬排序"])
        if indu_salary_selected:
            st.write(f"#### {indu_salary_selected}")
            st.dataframe(df_indu_salary_grouped.sort_values(
                by={"按最低薪酬排序": "min_salary", "按平均薪酬排序": "mid_salary", "按最高薪酬排序": "max_salary"}.get(
                    indu_salary_selected, "min_salary"),
                ascending=False),
                hide_index=True,
                use_container_width=True,
                column_config={"industry": "行业", "min_salary": "最低薪酬", "mid_salary": "平均薪酬", "max_salary": "最高薪酬"})
    st.write("### 2.2 岗位分析")
    with st.expander("2.2.1 按城市"):
        st.write("开发中..")

    with st.expander("2.2.2 按薪酬"):
        st.write("开发中..")

    st.write("### 2.3 技能关键词分析")
    with st.expander("2.3.1 按城市"):
        st.write("开发中..")
    with st.expander("2.3.2 按薪酬"):
        st.write("开发中..")

    st.write("### 2.4 其他关键词分析")
    st.write("开发中..")


if __name__ == "__main__":
    # streamlit run main.py
    main()
