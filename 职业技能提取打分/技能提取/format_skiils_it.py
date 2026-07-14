import json
content = []
data = open("THUOCL_it.txt","r",encoding="utf-8").readlines()

"""
结构如下，仅提取关键词到content即可
字符串 	 395499
初始化 	 372767
数组 	 357924
...
"""
for line in data:
    line = line.strip()
    if line:
        content.append(line.split("\t")[0].strip())

with open("THUOCL_it.json","w",encoding="utf-8") as f:
    json.dump(content,f,ensure_ascii=False,indent=4)
