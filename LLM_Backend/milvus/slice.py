import json
import os
import logging
from sentence_transformers import SentenceTransformer
import torch
import torch.nn.functional as F
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
import nltk

# 下载 nltk 数据包
nltk.download('punkt')
nltk.download('punkt_tab')

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 配置 Milvus 参数
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "college_notifications"
EMBEDDING_DIMENSION = 1024  # 根据模型输出调整
CACHE_FOLDER = "./model"

# 初始化 Milvus 连接
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

# 定义 Milvus 集合 schema
def create_collection(collection_name, dimension=EMBEDDING_DIMENSION):
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="date", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="link", dtype=DataType.VARCHAR, max_length=1000),
        FieldSchema(name="chunk", dtype=DataType.VARCHAR, max_length=12000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dimension),
    ]

    schema = CollectionSchema(fields, description="College Notifications Collection")

    collection = Collection(name=collection_name, schema=schema)

    # 创建索引
    index_params = {
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128},
        "metric_type": "L2",
    }
    collection.create_index(field_name="embedding", index_params=index_params)

    return collection

# 创建或加载集合
if not utility.has_collection(COLLECTION_NAME):
    collection = create_collection(COLLECTION_NAME)
else:
    collection = Collection(name=COLLECTION_NAME)

# 初始化 Embedding 模型
relative_path = "./model/models--jinaai--jina-embeddings-v3"
absolute_path = os.path.abspath(relative_path)
# model = SentenceTransformer(absolute_path, trust_remote_code=True, cache_folder=CACHE_FOLDER)
model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, cache_folder=CACHE_FOLDER)

# 文本切片函数
def split_text(text, max_tokens=2048, max_length=7000):
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + ' '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ' '
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# 加载爬取的通知数据
def load_notifications(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        logging.error(f"Error loading file {file_path}: {e}")
        return []

# 生成 Embedding 向量
def generate_embeddings(texts, task="text-matching"):
    embeddings = model.encode(texts, task=task)
    # 归一化向量
    print("Shape of embeddings before normalization:", embeddings.shape)
    embeddings = F.normalize(torch.tensor(embeddings), p=2, dim=1).numpy()
    return embeddings

# 插入数据到 Milvus
def insert_into_milvus(collection, notifications):
    try:
        titles = []
        dates = []
        links = []
        chunks = []
        embeddings = []

        for notification in notifications:
            title = notification['title']
            date = notification['date']
            link = notification['link']
            content = notification['content']
            chunks_split = split_text(content)
            
            # 跳过 content=0 的情况
            if len(chunks_split) == 0:
                logging.warning(f"Skipping notification with empty content: {title}")
                continue

            emb = generate_embeddings(chunks_split)
            for chunk, vector in zip(chunks_split, emb):
                titles.append(title)
                dates.append(date)
                links.append(link)
                chunks.append(chunk)
                embeddings.append(vector.tolist())

        # 构建数据
        entities = [
            titles,
            dates,
            links,
            chunks,
            embeddings,
        ]

        # 批量插入数据
        batch_size = 1000
        for i in range(0, len(titles), batch_size):
            batch_entities = [
                titles[i:i+batch_size],
                dates[i:i+batch_size],
                links[i:i+batch_size],
                chunks[i:i+batch_size],
                embeddings[i:i+batch_size],
            ]
            collection.insert(batch_entities)
            logging.info(f"Inserted batch {i//batch_size + 1} of {len(titles)//batch_size + 1}")

        # 刷新集合，确保数据可搜索
        collection.load()
        logging.info("Data inserted into Milvus successfully.")
    except Exception as e:
        logging.error(f"Error inserting data into Milvus: {e}")

# 示例用法
if __name__ == "__main__":
    # 假设通知数据存储在 result/kyjs.json 和 result/yunfeng/content1.json 等
    result_dir = "../result"
    notifications_files = []
    for root, dirs, files in os.walk(result_dir):
        for file in files:
            if file.endswith('.json'):
                notifications_files.append(os.path.join(root, file))

    all_notifications = []
    for file_path in notifications_files:
        notifications = load_notifications(file_path)
        # 如果文件包含多个通知，确保加载所有
        if isinstance(notifications, list):
            all_notifications.extend(notifications)
        else:
            all_notifications.append(notifications)

    insert_into_milvus(collection, all_notifications)