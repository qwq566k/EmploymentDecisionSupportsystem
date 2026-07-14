# coding:utf-8
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_path = "./results/checkpoint-11500"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForSequenceClassification.from_pretrained(model_path,num_labels=5)
model.eval() # 推理模式

test_data = {"text": "岗位职责：1.构架订单系统，实现自动出票，退票改签等\n2.构架财务系统，实现自动对账\n任职要求：1.相关岗位三年以上工作经验，熟悉机票行业。\n2.熟悉各大ota接口，实现订单导入，工单，航变，政策导入等细节功能。\n3.熟悉python技术，能及时精准获取到航司官网，app，b2b等数据来源。\n4.熟悉航司相关产品与活动，协同研发/数据团队分析和制定业务策略，了解自动过程中的业务场景痛点，完成系统需求分析与功能拆分，提升产品效益", "keywords": ["订单系统构架","自动出票","退票改签","财务系统构架","自动对账","机票行业经验","OTA接口熟悉度","订单导入","工单处理","航变处理","政策导入","Python技术","数据获取","航司产品与活动了解","业务策略分析","系统需求分析","功能拆分","产品效益提升"]}

# 对测试数据进行编码
inputs = []
for keyword in test_data["keywords"]:
    encoding = tokenizer(
        test_data["text"],keyword,
        max_length=128,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    inputs.append(encoding)

# 将所有编码后的数据合并为一个批次
results = []
for encoding,keyword in zip(inputs,test_data["keywords"]):
    with torch.no_grad():
        outputs = model(**{k:v.to(model.device) for k,v in encoding.items()})
        score = torch.softmax(outputs.logits, dim=-1) # 计算每个标签概率
        importance = torch.argmax(score, dim=-1).item() # 获取最可能的标签（评分）
    results.append({"keywords": keyword, "prediction": int(importance)+1}) # 预测结果为1-5

print("推理结果如下：")
print(f"原文：{test_data['text']}\n\n关键词如下：\n")
for result in results:
    if result:
        print(f"{result['keywords']} -> {result['prediction']}")