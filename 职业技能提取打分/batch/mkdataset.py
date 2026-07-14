import json
import re

with open("data/raw.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)
with open("data/output_202501170446.jsonl", "r", encoding="utf-8") as f:
    output = f.readlines()


# 使用raw_data中的text与output中对应行组成用于模型训练的数据集

# 先提取output数据，再按custom_id排序
# output_data = []
# for line in output:
#     line = json.loads(line)
#     tmp = {"custom_id": line["custom_id"], "assistant":line["response"]["body"]["choices"]["message"]["content"]}
#     output_data.append(tmp)

# output_data.sort(key=lambda x: x["custom_id"])


def get_output_data(custom_id):
    for line in output:
        line = json.loads(line)
        if line["custom_id"] == custom_id:
            l:str = line["response"]["body"]["choices"][0]["message"]["content"]
            l = l.replace("```json\n","").replace("```","")
            try:
                l = json.loads(l)
            except:
                pass
            return l


dataset = []
err_data = open("data/err_data.json", "w", encoding="utf-8")
for i in range(len(output)):
    print(f"Processing {i+1}/{len(output)}", end="\r")
    assustant = get_output_data(f"request-{i+1}")
    if isinstance(assustant, str): # 代表当前数据无法解析
        err_data.write(f"request-{i+1}\n") # 写入错误数据
        continue
    if assustant["keywords"] == []: # 代表当前数据没有关键词
        continue # 跳过
    text = raw_data["rows"][i]["job_description"]
    annotation = []
    for item in assustant["keywords"]:
        match = re.search(re.escape(item["keyword"]),text)
        if match:
            annotation.append({"start": match.start(),
                               "end": match.end(),
                               "label": item["keyword"],
                               "score":item["importance"]
                               })
    dataset.append({"text": text,
                    "annotations": annotation})
json.dump(dataset, open("data/dataset.json", "w", encoding="utf-8"), ensure_ascii=False)
