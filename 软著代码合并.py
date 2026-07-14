# 本文件用于合并软著代码
import re
import os

files_list = [
    r"server\main.py",
    r"server\config.py",
    r"server\utils\get_tasks.py",
    r"server\utils\pyjwt.py",
    r"server\router\zhilian_router.py",
    r"server\router\bosszhipin_router.py",
    r"server\model\verify_model.py",
    r"server\model\result_model.py",
    r"server\model\db_model.py",
    r"server\db\__init__.py",
    r"zhilian\client.py",
    r"zhilian\config.toml",
    r"zhilian\资料\获取城市列表.js",
    r"zhilian\资料\获取职位列表.js",
    r"zhilian\资料\转换.py",
    r"zhilian\资料\getJoblist.js",
    r"bosszhipin\client.py",
    r"bosszhipin\config.toml",
    r"bosszhipin\资料\转换.py",
    r"bosszhipin\资料\getJoblist.js",
    r"bosszhipin\资料\joblist_format.py",
    r"预处理\db\__init__.py",
    r"预处理\数据库导出.py",
    r"预处理\数据库合并.py",
    r"数据分析\visualization.py",
    r"数据分析\word_count.py",
    r"数据分析\tools\sql2parquet.py",
    r"数据分析\export.py",
    r"职业技能提取打分\技能标注核对\server.py",
    r"职业技能提取打分\技能标注核对\index.html",
    r"职业技能提取打分\技能标注核对\导入数据库.py",
    r"职业技能提取打分\batch\mkdataset_dictbook.py",
    r"职业技能提取打分\batch\raw2jsonl.py",
    r"职业技能提取打分\train_v2\train.py",
    r"职业技能提取打分\train_v2\reasoning.py",
    r"客户端打包\智联\client.py",
    r"客户端打包\Boss直聘\client.py"
]

# 主要逻辑： 读取文件清除代码注释，清除空白行，最后合并文件内容

files_suffix = ["py", "js"]  # 需要合并的文件后缀
pass_files = ["config.toml", "requirements.txt", "README.md", "LICENSE", "index.html"]  # 不需要合并的文件
pass_path = [".venv"] # 无需扫描的文件夹

if not any(files_list):
    print("未自定义文件列表，开始自动搜索")
    for root, dirs, files in os.walk("."):
        if any([pass_dir in root for pass_dir in pass_path]):
            continue
        for file in files:
            if file.endswith(tuple(files_suffix)) and file not in pass_files:
                files_list.append(os.path.join(root, file))
    print(f"共找到 {len(files_list)} 个文件")
exit()
contents = ""
for file in files_list:
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        # 将非独立一行的注释转移到新的一行
        content = re.sub(r'(?<!\n)(#[^\n]*)', '\n<1>', content)
        # 清除URL
        content = re.sub(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', 'URL_PLACEHOLDER', content)
        # 清除注释
        # content = re.sub(r"(#[^\n]*)|(\'\'\'.*?\'\'\')|(\"\"\".*?\"\"\")", '', content, flags=re.DOTALL) # 清除单行和多行注释
        print(f"文件 {file} 合并成功，共 {len(content)} 字符")
        contents += content

# 清除空白行
content = re.sub(r'\n\s*\n', '\n', contents)
if os.path.exists("code.txt"):
    os.remove("code.txt")
with open("code.txt", "w", encoding="utf-8") as f:
    f.write(content)  # 将合并后的内容写入文件
lines = content.split("\n")
print(f"总共有 {len("".join(lines))} 字，有 {len(lines)} 行，可写 {len(lines)/50} 页")
