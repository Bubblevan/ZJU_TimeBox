import os
import json
import time
import requests
import torch
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from pymilvus import connections, Collection, utility
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置 Milvus 参数
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "college_notifications")
EMBEDDING_DIMENSION = 1024  # 根据模型输出调整

# 连接到 Milvus
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)
print(f"Connected to Milvus at {MILVUS_HOST}:{MILVUS_PORT}")

# 检查集合是否存在
if not utility.has_collection(COLLECTION_NAME):
    raise Exception(f"Collection {COLLECTION_NAME} does not exist. 请确保您已插入数据。")

# 加载集合
collection = Collection(name=COLLECTION_NAME)
print(f"Loaded Milvus collection: {COLLECTION_NAME}")

# 初始化 Embedding 模型
relative_path = "./model/models--jinaai--jina-embeddings-v3"
absolute_path = os.path.abspath(relative_path)
# model = SentenceTransformer(absolute_path, trust_remote_code=True)
model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, cache_folder="./model")
print("Initialized embedding model: jinaai/jina-embeddings-v3")

def split_text(text, max_tokens=800):
    """
    将文本切分为多个片段，每个片段不超过 max_tokens。
    """
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        # 简单按单词数切分
        if len(current_chunk.split()) + len(sentence.split()) <= max_tokens:
            current_chunk += sentence + '. '
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + '. '
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def generate_embeddings(texts, task="text-matching"):
    """
    生成文本的 Embedding 向量，并进行 L2 归一化。
    """
    embeddings = model.encode(texts, task=task)
    print(f"Generated embeddings for {len(texts)} texts.")
    # 归一化向量
    embeddings = F.normalize(torch.tensor(embeddings), p=2, dim=1).numpy()
    print("Normalized embeddings.")
    return embeddings

def generate_prompt(results, question):
    """
    根据检索到的结果和用户问题，生成用于 LLM 的 Prompt。
    """
    prompt = "使用标记中的内容作为你的知识:\n\n"
    # 加载集合到内存中
    collection.load()
    print("Loaded collection into memory for querying.")
    for hit in results:
        # 获取实体数据
        entity = collection.query(
            expr=f"id == {hit.id}",
            output_fields=["title", "date", "link", "chunk"]
        )
        if entity:
            entity = entity[0]
            prompt += f"标题: {entity.get('title', 'N/A')}\n时间: {entity.get('date', 'N/A')}\n链接: {entity.get('link', 'N/A')}\n内容: {entity.get('chunk', 'N/A')}\n\n"
        else:
            print(f"No entity found for ID: {hit.id}")
    # 释放集合
    collection.release()
    print("Released collection from memory.")
    
    prompt += (
        "回答要求：\n\n"
        "如果你不清楚答案，你需要澄清。\n"
        "避免提及你是从获取的知识。\n"
        "保持答案与中描述的一致。\n"
        "使用不分点的一段话(可使用分号)优化回答格式。\n"
        "使用与问题相同的语言回答。\n\n"
        f"问题: \"{question}\"\n"
    )
    print("Generated prompt for LLM.")
    return prompt


def get_answer_from_coze(prompt):
    """
    通过 Coze API 获取回答，支持流式响应。
    """
    API_URL = os.getenv("API_URL", "https://api.coze.cn/v3/chat")
    API_KEY = os.getenv("API_KEY", "pat_lh9minUw0dYuu6QHFIq7rz1kY6tkFv70Iiic766T3IGNn2PuxxZijAGdOh9ZFknb")
    BOT_ID = os.getenv("BOT_ID", "7435604864455442486")
    print(prompt)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "bot_id": BOT_ID,
        "user_id": "local_user",
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": prompt,
                "content_type": "text"
            }
        ]
    }

    print("Sending request to Coze API...")

    # Send the request with streaming enabled
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)

    # Check if the response was successful
    if response.status_code == 200:
        full_response = ""
        event_type = None  # 用于记录事件类型的变量
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("event:"):
                    event_type = decoded_line.split(":")[1].strip()
                elif decoded_line.startswith("data:"):
                    data = decoded_line.split(":", 1)[1].strip()
                    try:
                        # 尝试将 data 解析为 JSON
                        json_data = json.loads(data)
                        # 仅在 json_data 是字典的情况下处理内容
                        if isinstance(json_data, dict):
                            if event_type == "conversation.message.delta":
                                # 逐字输出内容
                                content = json_data.get("content", "")
                                print("Streaming content:", content)
                                full_response += content
                            elif event_type == "conversation.chat.completed":
                                print("Conversation completed.")
                                break
                    except json.JSONDecodeError:
                        print("Unable to parse line:", decoded_line)
        return full_response.strip()
    else:
        print(f"请求失败: {response.status_code}, {response.text}")
        return f"请求失败: {response.status_code}, {response.text}"


    
def answer_question(question):
    """
    根据用户问题，生成回答。
    """
    print(f"Processing question: {question}")
    
    # Load the collection into memory
    collection.load()
    print("Loaded collection into memory.")

    # 生成问题的 Embedding 向量
    question_embedding = generate_embeddings([question], task="text-matching")[0].tolist()
    print(f"Question embedding (first 5 dimensions): {question_embedding[:6]}")
    
    # 在 Milvus 中搜索相似的向量
    search_results = collection.search(
        data=[question_embedding],
        anns_field="embedding",
        param={"metric_type": "L2", "params": {"nprobe": 10}},
        limit=5,
        expr=None,
        output_fields=["id"]  # 只返回 id 字段
    )[0]
    
    print(f"Number of search results: {len(search_results)}")
    for hit in search_results:
        print(f"Hit ID: {hit.id}, Distance: {hit.distance}")
    
    # 检查是否有检索结果
    if not search_results:
        print("No search results found.")
        return "抱歉，我无法找到相关的通知信息。"
    
    # 构建 Prompt
    prompt = generate_prompt(search_results, question)
    
    # 获取回答
    answer = get_answer_from_coze(prompt)
    
    # Release the collection from memory if it's no longer needed
    collection.release()
    print("Released collection from memory.")

    return answer


if __name__ == "__main__":
    # 输出嵌入向量的维度
    embedding_field = next((field for field in collection.schema.fields if field.name == "embedding"), None)
    if embedding_field:
        print(f"Embedding Dimension: {embedding_field.params['dim']}")
    else:
        print("Embedding field not found in the collection schema.")

    while True:
        user_question = input("请输入您的问题（输入回车结束）：")
        if not user_question:
            break
        answer = answer_question(user_question)
        print(f"回答：\n{answer}\n")
