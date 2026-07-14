import json
import pymysql

data = json.load(open('dataset.json', 'r', encoding='utf-8'))

# 示例数据：
# [{"text": "职位名称:电气工程师 1.熟悉各电子元器件基本功能。2.了解常用的数字电路，模拟电路,懂得基本的使用方法3.会使用AUTO CAD、EPLAN等绘图软件。4.负责现场硬件系统方案设计、电路图、原理图、现场施工等。5.电子、自动化、通信及其相关专业，专科工作经验五年以上6. 能够编写智能化系统方案，熟悉智能化系统架构。7. 有过多个项目实施经验；配电柜制作经验，现场布线经验。8. 学习能力较强、勤奋，具备团队合作精神及良好的敬业精神。职责范围:1、客户现场产品测试、安装、维护、故障排除.2、产品推广和安装使用培训.3、针对客户需求，做好售前的技术支持工作。4、维护客户关系，并对客户满意度进行回馈.5、客户资料的整理、汇总.公司福利:公司免费提供住宿，有竞争力的薪水 五险一金 出差补贴 绩效奖金 业务提成公司网址：http://www.jscx2018.com/公司电话：400-9287769", "keywords": [{"start": 16, "end": 21, "label": "电子元器件", "score": 3}, {"start": 33, "end": 37, "label": "数字电路", "score": 3}, {"start": 38, "end": 42, "label": "模拟电路", "score": 3}, {"start": 57, "end": 65, "label": "AUTO CAD", "score": 3}, {"start": 66, "end": 71, "label": "EPLAN", "score": 3}, {"start": 141, "end": 148, "label": "智能化系统方案", "score": 3}, {"start": 151, "end": 158, "label": "智能化系统架构", "score": 3}, {"start": 173, "end": 178, "label": "配电柜制作", "score": 2}, {"start": 181, "end": 185, "label": "现场布线", "score": 2}]},{...},...]

conn = pymysql.connect(host='localhost', user='root', password='123456', database='dataset')
cursor = conn.cursor()


for item in data:
    sql = "INSERT INTO dataset (text, keywords) VALUES (%s, %s)"
    cursor.execute(sql, (item['text'], json.dumps(item['keywords'], ensure_ascii=False)))
    conn.commit()
print("数据导入完成")

cursor.close()
conn.close()