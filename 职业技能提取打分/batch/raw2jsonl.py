# 将从数据库导出的json结构化数据转换为大模型Batch任务的jsonl文件
import json
import pandas as pd

Prompt_old = """
# 角色定位：资深职业数据分析专家

您是一位拥有丰富经验的职业数据分析专家，擅长从复杂数据中提炼关键洞见。本次任务将发挥您的专业技能，对岗位招聘职位描述进行深入分析。

# 需要提取的文本：
【TEXT】

# 任务详情

1. 文本解析：请仔细阅读并分析提供的岗位招聘职位描述文本。
2. 技能标签提取：从中准确提取所有涉及的职业技能标签。
3. 技能重要性评分：
   - 根据文本上下文内容，对每个提取的技能标签进行1-5分的评分。
   - 分数越高，表示该技能在岗位描述中的重要性越高。
   - 如无法准确判断某技能的重要性，则默认评分为3。
4. 输出格式要求：
   - 严格按照指定的JSON格式输出，包含`label`（技能标签）和`level`（重要性评分）两个字段。
   - 无需包含任何其他信息或注释。
5. 输出完整性：确保输出包含所有提取的技能标签及其评分。

# 字段定义与输出示例
[
    {"label": "技能标签1", "level": 5},
    {"label": "技能标签2", "level": 4},
    ...
]


**示例说明**：

- **示例1**：
  - 输入文本：熟练掌握Python编程，具备Django或Flask框架经验，熟悉Linux操作系统。
  - 输出结果：
    [
        {"label": "Python编程", "level": 5},
        {"label": "Django框架", "level": 4},
        {"label": "Flask框架", "level": 4},
        {"label": "Linux操作系统", "level": 4}
    ]

- **示例2**：
  - 输入文本：熟悉SQL，有MySQL和Oracle数据库使用经验，具备良好的数据清洗和分析能力。
  - 输出结果：
```json
    [
        {"label": "SQL", "level": 5},
        {"label": "MySQL数据库", "level": 4},
        {"label": "Oracle数据库", "level": 4},
        {"label": "数据清洗", "level": 4},
        {"label": "数据分析", "level": 4}
    ]
```
# 执行任务

请根据上述要求，对提供的岗位招聘职位描述文本进行分析，并输出相应的技能标签及其重要性评分。您的决策将对职业分析模型的训练产生重要影响。
"""


Prompt = """
输入文本：【TEXT】

---

### 任务目标
从招聘文本中提取**具体技术实体**，仅限以下类别，并分配重要性评分。
**禁止提取抽象概念、软技能或流程性描述**。


### 关键词范围与示例
|类别|允许提取内容|示例|
|编程语言| 具体语言名称| Python, Java, C++, Rust, Go, SQL|
|框架/库| 开发框架、第三方库   | Spring Boot, React, TensorFlow, PyTorch, NumPy, Pandas|
|开发工具 | IDE、版本控制、构建工具| VS Code, IntelliJ IDEA, Git, Jenkins, Webpack, Docker|
|测试方法|测试框架、工具| JUnit, Selenium, Jest, Postman, pytest, LoadRunner |
|设计模式|具体模式名称| MVC, Singleton, Observer, Factory, Microservices  |
|算法|算法名称或核心技术|Dijkstra算法, 动态规划, 机器学习算法（如SVM、K-means)|
|数据库技术|数据库系统、查询语言、工具| MySQL, MongoDB, Redis, PostgreSQL, SQLAlchemy, Hibernate|
|前端优化技术|具体优化工具或技术|Webpack代码压缩, CDN加速, React虚拟DOM, Lighthouse性能分析|
|协议与标准|网络协议、技术标准| HTTP/2, RESTful API, gRPC, GraphQL, OAuth 2.0|
|云平台与运维|云服务商、运维工具| AWS EC2, Kubernetes, Terraform, Ansible, Prometheus|


### 严格排除内容
|类别|禁止提取内容示例|
|---|---|
|抽象概念|性能优化、可维护性、可扩展性、浏览器兼容性、代码规范 |
|软技能|沟通能力、团队合作、学习能力、问题解决能力|
|流程性描述|需求分析、文档编写、技术沉淀、单元测试（未提及具体工具如JUnit)|
|泛化术语|Web标准、前端性能、系统设计、软件开发（需明确技术如“敏捷开发”可提取)|
|非技术性名词|工作年限、学历要求、薪资范围、公司福利|


### 评分规则
|分值|定义|示例|
|---|---|---|
|3| 岗位核心要求，明确列为必备技能| Java开发岗中的“Java”，深度学习岗中的“PyTorch”|
|2| 高频出现的重要技能 | 全栈开发岗中的“React”，数据工程师岗中的“Spark” |
|1| 补充性技能或可选要求 | 前端岗中提到的“TypeScript”，测试岗中提到的“Cypress”|


### **格式与逻辑规则**
1. 原文保留原则
   - 保留原始大小写和符号（如“C#”“.NET Core”）。
   - 多词术语需完整提取（如“Spring Boot”而非“Spring”或“Boot”）。
2. 去重与合并
   - 合并变体（如“JS”和“JavaScript”仅保留后者）。
   - 排除非技术缩写（如“UI”需结合上下文，仅当明确指“UI框架”时提取）。
3. 非中文词汇保护
   - 若原文含“3D建模”“Power BI”等混合术语，需原样保留，禁止分词错误。


### 输出示例
输入文本：
招聘全栈工程师，要求精通Java和Spring Boot，熟悉MySQL数据库设计与优化，有微服务架构（如Dubbo）经验。掌握React前端框架，了解Webpack构建工具者优先。


输出：
```json
{
    "keywords": [
        {"keyword": "Java", "score": 3},
        {"keyword": "Spring Boot", "score": 3},
        {"keyword": "MySQL", "score": 2},
        {"keyword": "微服务架构", "score": 2},
        {"keyword": "Dubbo", "score": 1},
        {"keyword": "React", "score": 2},
        {"keyword": "Webpack", "score": 1}
    ]
}
```


### 错误案例修正
错误输入：
熟悉前端性能优化，包括浏览器兼容性处理和代码可维护性提升。


错误输出：
```json
{"keywords": [{"keyword": "前端性能优化", "score": 1}]}  // 违反规则！此为抽象概念
```


正确输出：
```json
{"keywords": []}  // 未提及具体技术（如Webpack/Lighthouse）
```
"""

# 遵循以下结构输出
# {
#     "custom_id": "request-1", #每个请求必须包含custom_id且是唯一的，用来将结果和输入进行匹配
#     "method": "POST",
#     "url": "/v4/chat/completions",
#     "body": {
#         "model": "glm-4", #每个batch文件只能包含对单个模型的请求,支持 glm-4-0520 glm-4-air、glm-4-flash、glm-4、glm-3-turbo.
#         "messages": [
#             {"role": "system","content": "你是一个意图分类器."},
#             {"role": "user", "content": """
#             # 任务：对以下用户评论进行情感分类和特定问题标签标注，只输出结果，
#             # 评论：review = "订单处理速度太慢，等了很久才发货。"
#             # 输出格式：
#             {
#             "分类标签": " ",
#             "特定问题标注": " "
#             }
#             """
#             }
#         ],
#         "temperature": 0.1
#     }
# }


def main(model: str):
    with open("data/raw.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"共有{len(data)}条数据")
    with open("data/data.jsonl", "w", encoding="utf-8") as f:
        id = 1
        for item in data["rows"]:
            f.write(json.dumps({
                "custom_id": f"request-{id}",
                "method": "POST",
                "url": "/v4/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "你是一个资深职业数据分析专家，擅长从复杂数据中提炼关键洞见。本次任务将发挥您的专业技能，对岗位招聘职位描述进行深入分析。"},
                        {"role": "user", "content": Prompt.replace(
                            "【TEXT】", item["job_description"])}
                    ],
                    "temperature": 0.2
                }
            }, ensure_ascii=False) + "\n")
            id += 1


def main_xlsx(model: str):
    zhilian_data = pd.read_excel(
        "data/zhilian.xlsx").loc[:, ["job_name", "require_content"]]
    zhilian_data = zhilian_data.loc[(zhilian_data["job_name"].str.len(
        # BERT模型只能处理512个字符
    )+zhilian_data["require_content"].str.len()+5) <= 512].dropna()
    print(f"zhilian_data可用数据量：{len(zhilian_data)}")
    fojob_data = pd.read_excel(
        "data/51job.xlsx").loc[:, ["job_name", "require_content"]]
    fojob_data = fojob_data.loc[(fojob_data["job_name"].str.len(
        # BERT模型只能处理512个字符
    )+fojob_data["require_content"].str.len()+5) <= 512].dropna()
    print(f"fojob_data可用数据量：{len(fojob_data)}")
    # 随机各抽取5000条数据
    data = pd.concat([zhilian_data.sample(5000), fojob_data.sample(5000)])
    data.reset_index(drop=True, inplace=True)
    # 用于记录request-id和对应的职业描述原文
    dictbook = open("data/dictbook.jsonl", "w", encoding="utf-8")
    dictdata = []
    with open(f"data/data.jsonl", "w", encoding="utf-8") as f:
        for index, row in data.iterrows():
            print(f"\r{index}", end=" ")
            f.write(json.dumps({
                "custom_id": f"request-{index}",
                "method": "POST",
                "url": "/v4/chat/completions",
                "body": {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "你是一个资深职业数据分析专家，擅长从复杂数据中提炼关键洞见。本次任务将发挥您的专业技能，对岗位招聘职位描述进行深入分析。"},
                        {"role": "user", "content": Prompt.replace(
                            "【TEXT】", f"职位名称:{row['job_name']} {row['require_content']}")}
                    ],
                    "temperature": 0.2
                }
            }, ensure_ascii=False) + "\n")
            dictdata.append(
                {
                    f"request-{index}": f"职位名称:{row['job_name']} {row['require_content']}"
                })
    dictbook.write(json.dumps(dictdata, ensure_ascii=False))
    dictbook.close()


if __name__ == "__main__":
    model = "glm-4-flash"
    main_xlsx(model)
