import json
import re
from typing import List

with open("data/dictbook.json", "r", encoding="utf-8") as f:
    raw_data:List[dict] = json.load(f)
with open("data/output_202502121536.jsonl", "r", encoding="utf-8") as f:
    output = f.readlines()

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

for i in range(len(output)):
    print(f"Processing {i+1}/{len(output)}", end="\r")
    assustant = get_output_data(f"request-{i}")
    if isinstance(assustant, str): # 代表当前数据无法解析
        continue
    if assustant["keywords"] == []: # 代表当前数据没有关键词
        continue # 跳过

    text = raw_data[i][f"request-{i}"]
    annotation = []
    for item in assustant["keywords"]:
        match = re.search(re.escape(item["keyword"]),text)
        if match:
            annotation.append({"start": match.start(),
                               "end": match.end(),
                               "label": item["keyword"],
                               "score":item["score"]
                               })
    dataset.append({"text": text,
                    "keywords": annotation})
json.dump(dataset, open("data/dataset.json", "w", encoding="utf-8"), ensure_ascii=False)
