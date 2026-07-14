import json


data = json.load(open("boss_skills.json","r",encoding="utf-8"))

content = []

def parse(obj:dict,level:int=1):
    global content
    for item in obj:
        if item["name"]:
            content.append(item['name'])
        if item.get("subLevelModelList"):
            parse(item["subLevelModelList"],level+1)

for item in data:
    content.append(item['name'])
    parse(item["subLevelModelList"])

json.dump(content,open("boss_skills.json","w",encoding="utf-8"),ensure_ascii=False,indent=4)