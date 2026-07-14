import json

data = {"city_list": {}, "hot_city_list": {}, "job_list": []}


def citylist_format():
    with open("raw_citylist.json", "r", encoding="utf-8") as f:
        citylist = json.load(f)
        cityGroup = citylist["zpData"]["cityGroup"]
        hotCityList = citylist["zpData"]["hotCityList"]
        for category in cityGroup:
            for city in category["cityList"]:
                data["city_list"][city["name"]] = {
                    "code": city["code"], "cityCode": city["cityCode"]}

        for city in hotCityList:
            data["hot_city_list"][city["name"]] = {
                "code": city["code"], "cityCode": city["cityCode"]}


def joblist_format():
    with open("raw_joblist.json", "r", encoding="utf-8") as f:
        joblist = json.load(f)
        jobData = joblist["zpData"]
        for category in jobData:
            data["job_list"].append({
                "category": category["name"],
                "code": category["code"],
                "items": [{"code": item["code"], "name": item["name"]} for item in category["subLevelModelList"]]
            })

citylist_format()
joblist_format()
with open("bosszhipin.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
