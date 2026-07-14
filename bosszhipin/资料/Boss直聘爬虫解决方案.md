## BOSS直聘 爬虫解决方案

### 爬取流程

1. 通过服务端获取爬取的职位以及地点

2. 判断是否登录
   
   - https://www.zhipin.com/wapi/zpuser/wap/getUserInfo.json
   
   - 可能需要劝告用户退出登录，避免影响账号权重及扰乱未来正常使用的系统推荐

3. 翻页爬取职位信息列表 
   
   - https://www.zhipin.com/wapi/zpgeek/search/joblist.json

4. 通过由 <u>步骤3</u>  获取的 `securityId`  `lid`获取职位详情介绍，与步骤3数据合并 或 后续更新
   
   - https://www.zhipin.com/wapi/zpgeek/job/card.json

5. 通过由 步骤3 获取的 `encryptBrandId`  获取公司详情介绍，与步骤3数据合并 或 后续更新

### 备注

1. BOSS直聘为业界内反爬能力顶端之一，反反爬手段与技术目前已确定，但爬取速率尚未测试，进行爬取时速率应当谨慎，小心触发反爬机制。

2. 该站与其他站点相比，反爬攻破难度高，单次爬取时间较长。但鉴于该站数据价值更高、单次爬取数据量大（单页30条），因此仍为重点爬取目标。


