from transformers import AlbertForSequenceClassification, Trainer, TrainingArguments,AutoTokenizer
from sklearn.model_selection import train_test_split
import json
import os
import torch
from torch.utils.data import Dataset


MODEL_PATH = "voidful/albert_chinese_base"
PROXYS = {"http":"http://192.168.151.194:7890","https":"http://192.168.151.194:7890"}

tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH,proxies=PROXYS) # 加载tokenizer
model = AlbertForSequenceClassification.from_pretrained(MODEL_PATH,num_labels=5,proxies=PROXYS) # 加载模型

class KeywordDataset(Dataset):
    def __init__(self, data):
        self.data = data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        item = self.data[index]
        # 确保返回包含 input_ids 和 attention_mask 的数据
        return {
            "input_ids": item["input_ids"],
            "attention_mask": item["attention_mask"],
            "labels": torch.tensor(item["importance"]-1, dtype=torch.long)
        }

def load_data():
    print("正在加载数据...")

    with open("dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. 合成数据样本
    print("正在处理数据...")
    processed_data = []
    for item in data:
        text = item["text"]
        for annotation in item["assistant"]:
            try:
                processed_data.append({
                    "text": text,
                    "keyword": annotation["label"],
                    "importance": annotation["level"]
                })
            except:
                pass

    # 2. 构造ALBERT输入数据
    print("正在构造输入数据...")
    inputs = []  # 用于存储处理后的数据
    for item in processed_data:
        text = item["text"]
        keyword = item["keyword"]
        encoding = tokenizer(
            text, keyword,
            max_length=128,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        inputs.append({
            "input_ids": encoding["input_ids"].squeeze(0),  # 去掉 batch 维度
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "importance": item["importance"]
        })

    # 3. 数据划分
    print("正在划分数据集...")
    train_data, test_data = train_test_split(inputs, test_size=0.2, random_state=42)
    val_data, test_data = train_test_split(test_data, test_size=0.5, random_state=42)

    # 将划分后的数据转换为 Dataset
    train_data = KeywordDataset(train_data)
    val_data = KeywordDataset(val_data)
    test_data = KeywordDataset(test_data)
    print(f"训练集大小：{len(train_data)}，验证集大小：{len(val_data)}，测试集大小：{len(test_data)}")

    return train_data, val_data, test_data




def load_trainer(train_data,val_data):

    # for param in model.albert.embeddings.parameters():
    #     param.requires_grad = False # 冻结embedding层

    training_args = TrainingArguments(
        output_dir="./results",
        num_train_epochs=3,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        weight_decay=0.01,
        logging_dir='./logs',
        logging_steps=10,
        evaluation_strategy="epoch",
        learning_rate=2e-5,
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_data,
        eval_dataset=val_data,
        tokenizer=tokenizer
    )
    return trainer

if __name__ == "__main__":
    train_data,val_data,test_data = load_data()
    trainer = load_trainer(train_data,val_data)
    trainer.train()
    results = trainer.predict(test_data)
    print(results)
