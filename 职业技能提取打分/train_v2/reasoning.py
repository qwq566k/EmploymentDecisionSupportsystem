# -*- coding: utf-8 -*-
import json
import torch
from transformers import AutoTokenizer
import numpy as np
import random
from train import MultiTaskBert  # 确保 train.py 里的 MultiTaskAlbert 已正确导入
from torch.quantization import quantize_dynamic
import re

# 加载模型和 tokenizer
PROXYS = {"http": "http://192.168.10.27:7890",
          "https": "http://192.168.10.27:7890"}
model_path = "./results/xlm-roberta-base"  # 模型路径 /checkpoint-2600
tokenizer_path = "xlm-roberta-base"
tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
model = MultiTaskBert.from_pretrained(
    model_path, ignore_mismatched_sizes=True)
model = quantize_dynamic(model, {torch.nn.Linear})  # 动态量化
model.eval()  # 进入推理模式

def merge_subwords(tokens, labels):
    merged = []
    current_term = []
    for token, label in zip(tokens, labels):
        if label in [1, 2]:  # B-KW或I-KW
            if token.startswith("##"):
                current_term.append(token[2:])  # 去除##前缀
            else:
                if current_term:
                    merged.append("".join(current_term))
                current_term = [token]
        else:
            if current_term:
                merged.append("".join(current_term))
                current_term = []
    if current_term:
        merged.append("".join(current_term))
    return merged


def post_process(extracted):
    filtered = []
    exclude_patterns = {"的", "是", "在", "和", "与", "或", "等", "有", "为", "中", "对", "对于",
                        "关于", "通过", "基于", "使用", "使用了", "使用的", "使用了", "优化", "优化了", "优化的", "优化了", "进行", "进行了", "进行的", "进行了", "分析", "管理", "能力"}
    for kw in extracted:
        if kw in exclude_patterns or (len(kw) == 1 and kw in exclude_patterns):
            continue
        filtered.append(kw)
    return filtered


def infer(text):
    inputs = tokenizer(text, return_tensors="pt",
                       padding=True, truncation=True, max_length=512)
    with torch.no_grad():
        outputs = model(**inputs)
        ner_logits = outputs["ner_logits"]
        score_preds = outputs["score_preds"]

    ner_predictions = torch.argmax(ner_logits, dim=-1).squeeze().tolist()
    tokenized_text = tokenizer.convert_ids_to_tokens(
        inputs["input_ids"].squeeze().tolist())
    score_preds = score_preds.squeeze().tolist()

    extracted_keywords = []
    scores = []
    current_kw_tokens = []
    current_labels = []
    current_scores = []

    for i, (token, label) in enumerate(zip(tokenized_text, ner_predictions)):
        # print(i, token, label, score_preds[i])
        if token in ["[CLS]", "[SEP]", "[PAD]"]:
            continue
        if label == 1:  # B-KW
            if current_kw_tokens:
                merged_kw = merge_subwords(current_kw_tokens, current_labels)
                if merged_kw:
                    extracted_keywords.append("".join(merged_kw))
                    scores.append(np.max(current_scores))
            current_kw_tokens = [token]
            current_labels = [label]
            current_scores = [1 + 2 * score_preds[i]]
        elif label == 2:  # I-KW
            current_kw_tokens.append(token)
            current_labels.append(label)
            current_scores.append(score_preds[i])
            # current_scores.append(1 + 2 * score_preds[i])
        else:  # O
            if current_kw_tokens:
                merged_kw = merge_subwords(current_kw_tokens, current_labels)
                if merged_kw:
                    extracted_keywords.append("".join(merged_kw))
                    # 使用最大值
                    scores.append(np.max(current_scores))
            current_kw_tokens = []
            current_labels = []
            current_scores = []
    if current_kw_tokens:
        merged_kw = merge_subwords(current_kw_tokens, current_labels)
        if merged_kw:
            extracted_keywords.append("".join(merged_kw))
            scores.append(np.max(current_scores))
    extracted_keywords = post_process(extracted_keywords)
    scores = [np.clip(s, 1.0, 3.0) for s in scores]  # 硬性约束
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {"input_text":text,"keywords": [{"keyword": kw, "score": round(s, 2)} for kw, s in zip(extracted_keywords, scores)], "avg_score": avg_score}

# 更好的打印结果


def print_result(result):
    input_text = result["input_text"]
    keywords = result["keywords"]
    # 匹配关键词位置并高亮
    for kw in keywords:
        start = input_text.find(kw["keyword"])
        if start != -1:
            end = start + len(kw["keyword"])
            input_text = f"{input_text[:start]}\033[32;4m{input_text[start:end]}\033[0m{input_text[end:]}"
    print(f"\n\n输入文本: {input_text}")
    print(f"平均评分: {result['avg_score']}")


# 测试
test_num = 3
data = json.load(open("data/dataset.json", "r", encoding="utf-8"))
texts = random.sample(data, test_num)
for text in texts:
    result = infer(text["text"])
    # print(result)
    print_result(result)
