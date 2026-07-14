import json

data = json.load(open("dataset.json","r",encoding="utf-8"))
content = []

for item in data:
    for k in item["keywords"]:
        content.append(k["label"].strip())

with open("dataset_skills.json","w",encoding="utf-8") as f:
    json.dump(content,f,ensure_ascii=False)