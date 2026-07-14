项目结构
    数据分析
    ├─ intest.py - 本文件用于单元开发 测试通过后的代码合入main.py
    ├─ jobinfo.parquet - jobinfo数据文件
    ├─ main.py - 主文件
    ├─ README.txt - 说明文件
    └─ tools - 工具类
       └─ sql2parquet.py - 将数据库的数据导出并预处理存入jobinfo.parquet中


【可视化】
	当前版本进度：
		✅ 1. 行业分析
			✅ 1.1 按城市
			✅ 1.2 按薪资
			🚧 1.3 重点行业
		🚧 2. 岗位分析
			🚧 2.1 按城市
			🚧 2.2 按薪资
			🚧 2.3 重点行业
		🚧 3. 技能关键词分析
			🚧 3.1 按薪资
			🚧 3.2 按数量
			🚧 3.3 重点行业


	项目运行
		以下文件可以直接用指令运行
		main.py / intest.py / sql2parquet.py
		$ streamlit run <文件名称>

	安装所需库
	> pip install streamlit dask[complete]