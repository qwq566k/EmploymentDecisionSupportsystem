# 珠三角就业决策支持系统

基于珠三角企业招聘与行业数据的**就业决策支持系统**：为高校决策者与学生提供行业选择、技能培养重点与岗位匹配建议。

仓库地址：[qwq566k/-](https://github.com/qwq566k/-)

## 项目简介

| 维度 | 说明 |
|------|------|
| 主要用户 | 高校决策人、学生 |
| 数据来源 | 招聘网站岗位信息、企业行业数据、高校就业数据 |
| 核心能力 | 分布式爬虫采集 → 清洗预处理 → 技能关键词抽取与打分 → 数据分析与可视化 |
| 主要技术 | Playwright 爬虫、FastAPI、MySQL、NLP / Transformers、Streamlit |

## 系统架构

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│ Boss直聘客户端   │────▶│                  │────▶│                 │
│ zhilian 智联客户端│────▶│  server 任务分发  │────▶│  MySQL 招聘库    │
└─────────────────┘     │  FastAPI 服务     │     └────────┬────────┘
                        └──────────────────┘              │
                                                          ▼
                        ┌──────────────────┐     ┌─────────────────┐
                        │ 职业技能提取打分  │◀────│ 预处理 / 数据分析 │
                        │ (训练 / 推理)     │     │ Streamlit 可视化  │
                        └──────────────────┘     └─────────────────┘
```

## 目录结构

```
├── server/                 # 爬虫任务分发与结果入库（FastAPI）
├── bosszhipin/             # Boss 直聘爬虫客户端
├── zhilian/                # 智联招聘爬虫客户端
├── 客户端打包/             # PyInstaller 打包源码与说明（不含编译产物）
├── 预处理/                 # 数据合并、导出、清洗脚本
├── 数据分析/               # 统计、词频/TF-IDF、Streamlit 可视化
├── 职业技能提取打分/       # 技能词典、批处理标注、模型训练与核对工具
│   ├── batch/              # 大模型批量标注与数据集构建
│   ├── 技能提取/           # 技能词典与格式化
│   ├── 技能标注核对/       # 人工核对 Web 工具
│   ├── train_v1/           # 初版训练（Albert 等）
│   └── train_v2/           # 多任务 XLM-RoBERTa 训练与推理
├── 资料/                   # 爬虫组规划文档
├── 项目概念.md             # 业务概念与模块分工
└── 低代码爬虫数据库结构.md # 数据库表结构说明
```

> 大体积数据（CSV / Parquet / Excel）、模型权重、`客户端打包` 编译产物、虚拟环境等已写入 `.gitignore`，需在本地自行准备或训练生成。

## 功能模块

### 1. 数据收集与清洗

- 多端爬虫客户端通过 JWT 从 `server` 领取任务并回传结果
- 支持任务超时回收、按平台（Boss / 智联）分发
- 预处理脚本完成合并、去重与导出

### 2. 技能提取与打分

- 基于职位描述做关键词（技能）抽取与重要度打分
- 批处理 + 人工核对构建训练集；`train_v2` 使用 XLM-RoBERTa 多任务模型
- 支持对新岗位描述做推理

### 3. 数据分析与可视化

- 行业 / 城市 / 薪资等维度分析
- Streamlit 看板（详见 `数据分析/README.txt`）

## 快速开始

### 环境要求

- Python 3.10+（技能训练建议使用独立虚拟环境）
- MySQL 8.x
- 爬虫客户端：已安装的 Chromium / Edge（Playwright）

### 1. 克隆仓库

```bash
git clone https://github.com/qwq566k/-.git
cd -
```

### 2. 配置数据库

参考 `低代码爬虫数据库结构.md` 建库建表。复制示例配置：

```bash
copy server\config.example.py server\config.py
copy 预处理\config.example.py 预处理\config.py
```

修改其中的 `MYSQL_URL_ASYNC`、`JWT_SECRET` 等。

### 3. 启动任务服务端

```bash
cd server
pip install fastapi uvicorn sqlalchemy aiomysql aiocache pyjwt pydantic
uvicorn main:app --host 0.0.0.0 --port 12453
```

### 4. 运行爬虫客户端

分别编辑 `bosszhipin/config.toml`、`zhilian/config.toml` 中的 `base_url`，安装依赖后运行：

```bash
pip install playwright loguru requests pydantic tomli
playwright install
python bosszhipin/client.py
# 或
python zhilian/client.py
```

### 5. 数据分析看板

```bash
cd 数据分析
pip install streamlit dask[complete] pandas
# 准备 data/jobinfo.parquet 或通过 tools/sql2parquet.py 导出
streamlit run visualization.py
```

### 6. 技能模型训练（可选）

模型权重体积大，不随仓库分发。在具备 GPU 的环境下：

```bash
cd 职业技能提取打分/train_v2
# 按需准备 data/dataset.json，配置 HF 镜像后运行
python train.py
```

## 安全说明

- **请勿**将真实数据库密码、生产 JWT 密钥、Cookies 提交到 Git
- 仓库内配置仅为本地占位；若历史提交中曾泄露凭据，请尽快在服务器侧轮换密码
- 爬虫仅供学习与科研场景使用，请遵守目标网站服务条款与当地法律法规

## 相关文档

- [项目概念](项目概念.md)
- [数据库结构](低代码爬虫数据库结构.md)
- [爬虫组任务规划](资料/爬虫组任务规划.md)
- [Boss 直聘爬虫方案](bosszhipin/资料/Boss直聘爬虫解决方案.md)

## License

仅供学习与课题研究使用。
