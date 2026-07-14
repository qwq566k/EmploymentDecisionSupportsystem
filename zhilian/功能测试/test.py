import requests
import time
import json

base_url = "http://localhost:8000"

# 1. 获取token
print("1. 获取token")
token = requests.get(
    base_url+"/token", params={"device_id": "WXP"}).json()["data"]
print(token["token"])


# 2. 获取task
print("\n\n2. 获取task")
task = requests.get(
    base_url+"/task", headers={"token": token["token"]}).json()["data"]
print(task)


# 3. 更新task状态
print("\n\n3. 更新task状态为2")
status = requests.post(base_url+"/task/update", json={
                       # 2表示正在执行
                       "task_id": task["id"], "status": 2}, headers={"token": token["token"]}).json()
print(status)


# 4. 使用FakeData模拟执行task
print("\n\n4. 使用FakeData模拟执行task")
data = json.load(open("智联招聘.json", 'r', encoding="utf-8"))
result = requests.post(
    base_url + "/result", json={"data":data, "task_id": task["id"],"platform":1}, headers={"token": token["token"]}).json()
print(result)

# 5. 完成爬取之后更新状态为1
print("\n\n5. 更新task状态为1")
fresh = requests.post(base_url+"/task/update", json={"task_id": task["id"], "status": 1},headers={"token": token["token"]}).json()
print(fresh)

print("\n\n测试完成")