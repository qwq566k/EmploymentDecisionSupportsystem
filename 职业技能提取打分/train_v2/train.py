# from matplotlib import pyplot as plt
# import seaborn as sns
# import pandas as pd
import json
import os
from collections import Counter

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import accuracy_score, mean_absolute_error
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from torch.optim import AdamW
from torch.utils.data import Dataset, WeightedRandomSampler
from transformers import (AutoTokenizer, BertModel, BertPreTrainedModel,
                          DataCollatorWithPadding, Trainer, TrainingArguments,
                          XLMRobertaModel, XLMRobertaPreTrainedModel)

os.environ['HF_HOME'] = '/root/autodl-tmp/cache/'
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

# Linux
# export HF_ENDPOINT=https://hf-mirror.com

# Windows PowerShell
# $env:HF_ENDPOINT = "https://hf-mirror.com"

# HF_ENDPOINT=https://hf-mirror.com

# ================== 模型定义 ==================


class Attention(nn.Module):
    def __init__(self, hidden_size):
        super().__init__()
        self.attn = nn.Linear(hidden_size, 1)  # 计算注意力得分

    def forward(self, sequence_output):
        # sequence_output: [batch_size, seq_len, hidden_size]
        attn_scores = self.attn(sequence_output)  # [batch_size, seq_len, 1]
        attn_weights = torch.softmax(attn_scores, dim=1)  # 归一化权重
        # [batch_size, hidden_size]
        context_vector = torch.sum(attn_weights * sequence_output, dim=1)
        return context_vector


class MultiTaskBert(XLMRobertaPreTrainedModel):
    def __init__(self, config):
        super().__init__(config)
        self.roberta = XLMRobertaModel(config)  # 替换 BertModel
        # 冻结前几层
        for param in self.roberta.embeddings.parameters():
            param.requires_grad = False
        for param in self.roberta.encoder.layer[:6].parameters():
            param.requires_grad = False

        self.ner_head = nn.Linear(config.hidden_size, 3)
        self.attention = Attention(config.hidden_size)
        self.score_head = nn.Sequential(
            nn.Linear(config.hidden_size * 2, 128),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(128, 1),
            nn.Sigmoid()
        )

    def forward(self, input_ids, attention_mask=None, bio_labels=None, score_labels=None, token_type_ids=None):
        outputs = self.roberta(input_ids, attention_mask=attention_mask)
        # [batch_size, seq_len, hidden_size]
        sequence_output = outputs.last_hidden_state

        # NER 任务
        ner_logits = self.ner_head(sequence_output)  # [batch_size, seq_len, 3]

        # 评分任务
        context_vector = self.attention(
            sequence_output)  # [batch_size, hidden_size]
        # 将全局上下文扩展到每个 token
        context_expanded = context_vector.unsqueeze(
            1).expand(-1, sequence_output.size(1), -1)
        # [batch_size, seq_len, hidden_size*2]
        fused_feature = torch.cat([sequence_output, context_expanded], dim=-1)
        score_preds = self.score_head(
            fused_feature).squeeze(-1)  # [batch_size, seq_len]
        score_preds = torch.clamp(score_preds, 0.0, 1.0)  # 映射前限制
        score_preds = 1 + 2 * score_preds  # 映射到 1-3

        return {
            "ner_logits": ner_logits,
            "score_preds": score_preds,
            "bio_labels": bio_labels,
            "score_labels": score_labels
        }


# ================== 损失函数 ==================
class BoundedMSELoss(nn.Module):
    def __init__(self, min_val=1.0, max_val=3.0):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.mse_loss = nn.MSELoss()

    def forward(self, preds, target):
        bounded_preds = torch.clamp(preds, self.min_val, self.max_val)
        return self.mse_loss(bounded_preds, target)


class DynamicWeightingLoss(nn.Module):
    def __init__(self):
        super().__init__()
        class_weights = torch.tensor([1.0,15.0,10.0]) # 根据标签频率调整权重
        self.ner_loss = nn.CrossEntropyLoss(weight=class_weights,ignore_index=-100)
        self.score_loss = BoundedMSELoss(min_val=1.0, max_val=3.0)
        self.alpha = nn.Parameter(torch.tensor(0.5))  # 可学习权重
        self.monentum = 0.9 # 动态权重更新速度

    def forward(self, ner_logits, score_preds, bio_labels, score_labels):
        ner_loss_val = self.ner_loss(
            ner_logits.view(-1, 3), bio_labels.view(-1))
        score_loss_val = self.score_loss(score_preds, score_labels)
        # 动态权重（0到1之间）
        alpha = torch.sigmoid(self.alpha) * 0.6 +0.2
        self.alpha.data = self.alpha.data * self.monentum + alpha * (1 - self.monentum)
        total_loss = alpha * ner_loss_val + (1 - alpha) * score_loss_val
        print(f"Alpha: {alpha.item():.3f} | NER Loss: {ner_loss_val:.3f} | Score Loss: {score_loss_val:.3f}")
        return total_loss

# ================== 数据预处理 ==================


def advanced_alignment(text, keywords, tokenizer):
    # 使用tokenizer对输入文本进行分词，并返回每个token的字符偏移量
    tokenized = tokenizer(text, return_offsets_mapping=True,
                          add_special_tokens=False)

    # 读取技术字典，该字典包含了一些技术词汇
    tech_vocab = json.load(open("data/skills.json", "r", encoding="utf-8"))
    # 创建一个字典，用于将字符位置映射到对应的token索引
    char2token = {}
    for idx, (start, end) in enumerate(tokenized.offset_mapping):
        if start != end:
            for i in range(start, end):
                char2token[i] = idx

    # 新增CRF层支持的标签体系
    char2token = {o[0]: i for i, o in enumerate(
        tokenized.offset_mapping) if o[0] != o[1]}

    # 初始化标签矩阵
    bio_labels = ["O"] * len(tokenized.input_ids)
    score_labels = [0.0] * len(tokenized.input_ids)
    for kw in keywords:
        if kw["label"] not in tech_vocab:
            continue

        start_char = kw["start"]
        end_char = kw["end"]

        start_token = char2token.get(start_char)
        end_token = char2token.get(end_char-1)

        if start_token is None or end_token is None:
            continue
        
        print(f"Keyword: {kw['keyword']} | Start-End: {start_char}-{end_char}")
        print(f"Token Span: {start_token}-{end_token} | Tokens: {tokenized.input_ids[start_token:end_token+1]}")
        
        token_str = tokenizer.decode(
            tokenized.input_ids[start_token:end_token+1])
        if token_str != kw["label"]:
            continue

        bio_labels[start_token] = "B-KW"
        for i in range(start_token+1, end_token+1):
            bio_labels[i] = "I-KW"

        # 分数传播策略
        base_score = kw["score"]
        for i in range(start_token, end_token+1):
            # 平方根衰减 + 起始 token 不衰减
            decay = 1.0 - ((i - start_token) / (end_token - start_token + 1)) ** 0.5
            if i == start_token:
                decay = 1.0
            score_labels[i] = max(score_labels[i], base_score * decay)

    return {
        "input_ids": tokenized["input_ids"],
        "bio_labels": bio_labels,
        "score_labels": score_labels
    }


# ================== 数据集类 ==================
class SkillDataset(Dataset):
    def __init__(self, data_path, tokenizer, load_file=False):
        if load_file:
            self.data = json.load(open(data_path, "r", encoding="utf-8"))
        else:
            self.data = data_path
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        processed = advanced_alignment(
            item["text"], item["keywords"], self.tokenizer)
        max_len = 512

        return {
            "input_ids": torch.tensor(processed["input_ids"][:max_len]),
            # 确保提供 attention_mask
            "attention_mask": torch.ones(len(processed["input_ids"][:max_len])),
            "bio_labels": torch.tensor(
                [["O", "B-KW", "I-KW"].index(l)
                 for l in processed["bio_labels"]],
                dtype=torch.long  # 确保 NER 标签是 Long 类型
            ),
            # 评分标签
            "score_labels": torch.tensor(processed["score_labels"], dtype=torch.float)
        }


# ================== 训练工具 ==================
def create_sampler(dataset):
    label_counts = Counter(
        [l for labels in dataset.bio_labels for l in labels])
    weights = [10.0 if l in [1,2] else 1.0 for labels in dataset.bio_labels for l in labels] # 1,2 类权重高
    return WeightedRandomSampler(weights, num_samples=len(weights))


def compute_metrics(p):
    ner_preds, score_preds = p.predictions
    ner_labels, score_labels = p.label_ids

    # 关键词检测指标
    active_mask = (ner_labels != -100)
    ner_accuracy = accuracy_score(
        ner_labels[active_mask],
        np.argmax(ner_preds, axis=-1)[active_mask]
    )

    # 评分回归指标（1-3范围）
    score_preds = np.clip(score_preds, 1.0, 3.0)  # 约束预测范围
    score_mae = mean_absolute_error(
        score_labels[active_mask],
        score_preds[active_mask]
    )

    return {
        "ner_acc": ner_accuracy,
        "score_mae": score_mae,
        "combined": ner_accuracy * 0.7 + (1 - score_mae / 2.0) * 0.3  # 归一化到0-1
    }


# ================== 程序入口 ==================
if __name__ == "__main__":
    MODEL_PATH = "xlm-roberta-large"  # "bert-base-chinese"
    TOKENIZER_PATH = "xlm-roberta-large"
    # TOKENIZER_PATH = "hfl/chinese-bert-wwm-ext"
    PROXYS = {"http": "http://192.168.10.27:7890",
              "https": "http://192.168.10.27:7890"}
    DATASET_PATH = "data/dataset.json"

    # 初始化组件
    tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_PATH, truncation=True)
    model = MultiTaskBert.from_pretrained(
        MODEL_PATH, ignore_mismatched_sizes=True)

    # 构建数据集
    dataset = SkillDataset(DATASET_PATH, tokenizer, load_file=True)
    train_data, eval_data = train_test_split(
        dataset.data, test_size=0.1, random_state=42)
    train_dataset = SkillDataset(train_data, tokenizer)
    eval_dataset = SkillDataset(eval_data, tokenizer)

    # ================== 自定义Collator ==================

    def custom_collator(data):
        data_collator = DataCollatorWithPadding(
            tokenizer=tokenizer,
            padding="max_length",
            max_length=512,
            return_tensors="pt"
        )

        # 对 input_ids 和 attention_mask 进行 padding
        collated = data_collator({
            "input_ids": [d["input_ids"] for d in data],
            "attention_mask": [d["attention_mask"] for d in data]
        })

        # 获取 batch 内的最大序列长度（经过 DataCollatorWithPadding 后所有样本的长度应该相同）
        max_seq_len = collated["input_ids"].shape[1]

        bio_labels = []
        score_labels = []
        for d in data:
            # 处理 bio_labels
            current_bio = d["bio_labels"]
            if len(current_bio) > max_seq_len:
                # 如果长度超过最大长度，则截断
                current_bio = current_bio[:max_seq_len]
            else:
                # 如果长度不足，则填充 -100
                pad_length = max_seq_len - len(current_bio)
                current_bio = torch.cat(
                    [current_bio, torch.full((pad_length,), -100, dtype=torch.long)])
            bio_labels.append(current_bio)

            # 处理 score_labels
            current_score = d["score_labels"]
            if len(current_score) > max_seq_len:
                current_score = current_score[:max_seq_len]
            else:
                pad_length = max_seq_len - len(current_score)
                current_score = torch.cat(
                    [current_score, torch.full((pad_length,), 0.0, dtype=torch.float)])
            score_labels.append(current_score)

        padded_bio = torch.stack(bio_labels)
        padded_score = torch.stack(score_labels)

        return {
            "input_ids": collated["input_ids"],
            "attention_mask": collated["attention_mask"],
            "bio_labels": padded_bio,
            "score_labels": padded_score
        }
    # ================== 自定义优化器 ==================

    def custom_optimizer(model):
        return AdamW(model.parameters(), lr=5e-5, weight_decay=0.05)

    # ================== 自定义训练器 ==================

    class MultiTaskTrainer(Trainer):
        def compute_loss(self, model, inputs, return_outputs=False,num_items_in_batch=None):
            bio_labels = inputs.get("bio_labels", None)
            score_labels = inputs.get("score_labels", None)

            outputs = model(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"]
            )
            ner_logits = outputs["ner_logits"]
            score_preds = outputs["score_preds"]

            # 确保 bio_labels 形状匹配
            # [batch_size, seq_length]
            if bio_labels.shape != ner_logits.shape[:2]:
                print(
                    f"Mismatch: ner_logits.shape={ner_logits.shape}, bio_labels.shape={bio_labels.shape}")
                bio_labels = bio_labels[:, :ner_logits.shape[1]]  # 截断

            # # 计算 NER 任务损失
            # loss_fct_ner = nn.CrossEntropyLoss(ignore_index=-100)
            # ner_loss = loss_fct_ner(
            #     ner_logits.view(-1, 3), bio_labels.view(-1))

            # # 计算 评分任务损失
            # loss_fct_score = BoundedMSELoss(min_val=1.0, max_val=3.0)
            # # loss_fct_score = nn.MSELoss()  # 使用均方误差损失函数
            # score_loss = loss_fct_score(score_preds, score_labels)

            # # 组合损失
            # loss = ner_loss * 0.5 + score_loss * 0.5

            dynamic_loss = DynamicWeightingLoss()  # 动态权重损失函数
            loss = dynamic_loss(
                ner_logits,
                score_preds,
                bio_labels,
                score_labels
            )
            return (loss, {"ner_logits": ner_logits, "score_preds": score_preds}) if return_outputs else loss
    # ================== 训练 ==================

    # ================== 训练配置 ==================
    training_args = TrainingArguments(
        output_dir="./results",
        per_device_train_batch_size=16,  # 提高 batch size（适配 2080Ti）
        gradient_accumulation_steps=4,  # 降低累积步数，提高更新频率
        fp16=True,  # 保持半精度训练，提升计算效率
        logging_steps=50,  # 更高频率的日志记录
        save_steps=200,  # 训练步数较大时，减少 checkpoint 频率
        save_total_limit=3,  # 保留最近 5 个 checkpoint
        evaluation_strategy="steps",
        eval_steps=200,  # 每 200 步进行一次评估
        warmup_ratio=0.1,  # 适度减少 warmup
        learning_rate=1e-5,  # 适当增加学习率，提高收敛速度
        weight_decay=0.1,  # 保持正则化，避免过拟合
        num_train_epochs=20,  # 2080Ti 训练更快，可以增加训练轮数
        logging_dir="/root/tf-logs",
        report_to=["tensorboard"],  # 继续使用 TensorBoard
        save_strategy="steps",
        load_best_model_at_end=True,  # 加载训练结束时的最佳模型
        metric_for_best_model="eval_loss",  # 根据验证集 loss 判断最佳模型
        greater_is_better=False,
        warmup_steps=500,  # 设置 warmup 步数
        lr_scheduler_type="cosine",  # 使用cosine调度
    )

    # 替换 Trainer
    trainer = MultiTaskTrainer(
        model=model,
        args=training_args,  # 训练参数
        train_dataset=train_dataset,  # 训练数据集
        eval_dataset=eval_dataset,  # 测试数据集
        compute_metrics=compute_metrics,  # 计算评估指标
        data_collator=custom_collator,  # 数据集合并器
        # 第一个是 optimizer，第二个是 scheduler
        optimizers=(custom_optimizer(model), None)

    )

    # 执行训练
    trainer.train()
    trainer.save_model("./results")
