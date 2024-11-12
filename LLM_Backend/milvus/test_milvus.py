import logging
from pymilvus import connections, Collection

# 配置日志记录
logging.basicConfig(level=logging.INFO)

# 配置 Milvus 参数
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"
COLLECTION_NAME = "college_notifications"

# 初始化 Milvus 连接
connections.connect("default", host=MILVUS_HOST, port=MILVUS_PORT)

# 加载集合
collection = Collection(name=COLLECTION_NAME)

# 查询集合中的数据数量
count = collection.num_entities
print(f"Number of entities in collection: {count}")

# 如果需要，可以进一步查询和打印数据
if count > 0:
    # 加载集合数据
    collection.load()
    
    # 查询前10条数据
    search_params = {
        "metric_type": "L2",
        "params": {"nprobe": 10},
    }
    results = collection.query(
        expr="id >= 0",
        output_fields=["id", "title", "date", "link", "chunk"],
        limit=10,
    )
    
    # 打印查询结果
    for result in results:
        print(result)

    # 释放集合数据
    collection.release()
else:
    print("No data found in the collection.")