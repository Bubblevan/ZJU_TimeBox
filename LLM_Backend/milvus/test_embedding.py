from sentence_transformers import SentenceTransformer

# 初始化模型并指定缓存目录
model = SentenceTransformer("jinaai/jina-embeddings-v3", trust_remote_code=True, cache_folder="./model")
# model = SentenceTransformer("./model/models--jinaai--jina-embeddings-v3", trust_remote_code=True, cache_folder="./model")

# 示例文本
texts = [
    "Follow the white rabbit.",  # 英文
    "Sigue al conejo blanco.",  # 西班牙文
    "Suis le lapin blanc.",      # 法文
    "跟着白兔走。",               # 中文
    "اتبع الأرنب الأبيض.",         # 阿拉伯文
    "Folge dem weißen Kaninchen.",  # 德文
]

# 生成 Embedding 向量
task = "text-matching"  # 根据需要选择任务
embeddings = model.encode(texts, task=task)

# 查看向量形状
print(embeddings.shape)  # 结果: (6, 1024)