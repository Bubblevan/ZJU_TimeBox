# -*- coding: utf-8 -*-

import pandas as pd
import jieba
import re
import os
from tqdm import tqdm
import json
import csv
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from classification import get_text_type
from train_text import get_train_text, add_train_texts

label2ind = {}


def get_paragraphs_by_split(text: str, sentences_per_paragraph=1):
    # 使用正则表达式来分割句子
    sentences = re.split('(。|！|!|\.)', text)
    new_sents = []
    # 按照指定的句子数量来分段
    paragraph = ""
    for i in range(int(len(sentences) / 2)):
        sent = sentences[2 * i] + sentences[2 * i + 1]
        paragraph += sent
        if (i + 1) % sentences_per_paragraph == 0 or (i + 1) == len(sentences) // 2:
            new_sents.append(paragraph.strip())
            paragraph = ""
    if paragraph:
        new_sents.append(paragraph.strip())
    return new_sents


def clean_paragraph(paras, stopwords_path):
    """
    清洗段落，去除标点符号，停用词，英文字符
    """
    new_paras = []
    # 读取停用词
    with open(stopwords_path, 'r', encoding='utf-8') as f:
        stopwords = set(f.read().splitlines())

    for each in paras:
        each = each.rstrip()
        each = each.replace('\n', '')
        each = each.replace('·', ' ')
        each = re.sub(r'\s+', ' ', each)
        each = re.sub(r'\b○\b', '零', each)
        each = each.replace('...', '…')
        each = each.replace('「', '“')
        each = each.replace('」', '”')
        punctuation_map = {',': '，', '!': '！', '?': '？', '(': '（', ')': '）', ':': '：', ';': '；'}
        for eng_punc, chi_punc in punctuation_map.items():
            each = each.replace(eng_punc, chi_punc)
        each = re.sub(r'[#$%&\'*/<=>@[\\]^_`{|}~]', '', each)
        words = jieba.cut(each)
        clean_words = [word for word in words if word not in stopwords and word.strip() != '']
        if len(clean_words) > 1:
            new_paras.append(" ".join(clean_words) + "\n")
    return new_paras

def preprocess():  # For FastText only
    """
    预处理文本，去除标点符号，停用词，英文字符
    """
    train_results = []
    file_path = "./output.json"
    processing_data = get_train_text(file_path)
    for row in processing_data:
        #print(row)
        content_id = row['content_id']
        content_text = row['content_text']
        paras = get_paragraphs_by_split(content_text, 1)
        paras = clean_paragraph(paras,"resources/stopwords")
        trained_text = []
        train_result = {
            #"分析文本": content_text,
            "叙述": 0,
            "情感共鸣": 0,
            "核心观点": 0,
            "细节描写": 0,
            "科学技术": 0,
            "通知报告": 0,
            "打标状态": "待打标",
            "其他": 0,
            "来源文本ID": content_id,
        }
        train_length = len(paras)
        for para in paras:
            train_type = get_text_type(para)
            train_content = {
                "分析文本": para,
                "叙述": train_type['叙述'],
                "情感共鸣": train_type['情感共鸣'],
                "核心观点": train_type['核心观点'],
                "细节描写": train_type['细节描写'],
                "科学技术": train_type['科学技术'],
                "通知报告": train_type['通知报告'],
                "打标状态": "待打标",
                "文本类型": train_type['最终类型'],
                "来源文本ID": content_id,
            }
            train_result['叙述'] += train_type['叙述'] / train_length
            train_result['情感共鸣'] += train_type['情感共鸣'] / train_length
            train_result['核心观点'] += train_type['核心观点'] / train_length
            train_result['细节描写'] += train_type['细节描写'] / train_length
            train_result['科学技术'] += train_type['科学技术'] / train_length
            train_result['通知报告'] += train_type['通知报告'] / train_length


            trained_text.append(train_content)
            #train_result[train_content['文本类型']] +=1/train_length
        train_results.append(train_result)
        # print(train_result)
        add_train_texts(trained_text,"resources/output.txt")
    return train_results

def preprocess_by_csv(file_path, out_path='resources/output.json'):
    """
    获取csv文件的内容
    """
    output = open(out_path, "w", encoding='utf-8', newline='')
    f = open(file_path, "r", encoding='utf-8')

    reader = csv.reader(f)
    next(reader)

    for row in reader:
        content_id = row[0]
        content_text = row[1]
        train_type = row[3]

        if train_type in ['钩子开头', '核心观点', '细节描述', '情感表达', '呼吁行动', '金句']:
            output.write(f"__label__{train_type}\t{content_text}\n")


if __name__ == '__main__':
    # 调用函数，指定输入和输出文件路径
    # input_file_path = ['./testset/Baola/']  # 这里更改为您的输入文件路径
    # output_file_path = './output.csv'  # 这里更改为您的输出文件路径
    # preprocess(input_file_path, output_file_path)

    # input_csv = './output.csv'
    # preprocess_by_csv(input_csv)
    preprocess()
