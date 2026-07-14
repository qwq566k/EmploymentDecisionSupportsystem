import json

data = json.load(open("raw_joblist.json","r",encoding="utf-8"))
for item in data["zpData"]:
    item:dict
    print(item["name"])
    if item.get("subLevelModelList") == None:
        continue
    for subitem in item["subLevelModelList"]:
        print("\t"+subitem["name"])