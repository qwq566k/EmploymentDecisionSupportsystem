
import json

data = json.load(open('raw.json','r',encoding='utf-8'))["city_list"]
new = {}
for typ in data: # 城市首字母
    for city in data[typ]: # 城市列表
        if not city['login']:
            new[city['name']] = city['code']

with open('city.json','w',encoding='utf-8') as f:
    json.dump(new,f,ensure_ascii=False)
print('转换完成')