import os
import json
import sqlite3
import requests

# 扣子 API 的 URL 和 API 密钥
API_URL = "https://api.coze.cn/v3/chat"
API_KEY = "pat_lh9minUw0dYuu6QHFIq7rz1kY6tkFv70Iiic766T3IGNn2PuxxZijAGdOh9ZFknb"

# 请求头
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# 连接到SQLite数据库
db_path = r"D:\MyLab\ZTB\ZJU_Calendar\LLM_Backend\spider1\notices.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 创建表的SQL模板
create_table_sql = '''
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    date TEXT,
    link TEXT,
    content TEXT
)
'''

# 检查标题是否已存在的SQL模板
check_title_sql = '''
SELECT COUNT(*) FROM {table_name} WHERE title = ?
'''

# 插入数据的SQL模板
insert_data_sql = '''
INSERT INTO {table_name} (title, date, link, content)
VALUES (?, ?, ?, ?)
'''

# 处理每个条目
def process_item(item, table_name):
    # 精简content字段
    payload = {
        "bot_id": "7435604864455442486",
        "user_id": "123123",
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": f"精简以下内容,保留关键信息(尤其是开始和结束时间)：{item['content']}.不用回答我也不用输出原文,直接输出120字以内精简后的一段话,不要分点.如果content内容为空,直接返回@@@",
                "content_type": "text"
            }
        ]
    }
    
    response = requests.post(API_URL, headers=headers, json=payload, stream=True)
    
    if response.status_code == 200:
        simplified_content = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("event:"):
                    event_type = decoded_line.split(":")[1].strip()
                elif decoded_line.startswith("data:"):
                    data = decoded_line.split(":", 1)[1].strip()
                    try:
                        json_data = json.loads(data)
                        if event_type == "conversation.message.delta":
                            simplified_content += json_data["content"]
                        elif event_type == "conversation.chat.completed":
                            print("对话历史:", json_data)
                    except json.JSONDecodeError:
                        print("无法解析的响应行:", decoded_line)
        
        # 如果精简后的内容不是@@@，则插入到SQLite数据库
        if simplified_content != "@@@":
            # 检查标题是否已存在
            cursor.execute(check_title_sql.format(table_name=table_name), (item['title'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute(insert_data_sql.format(table_name=table_name), (item['title'], item['date'], item['link'], simplified_content))
    else:
        print(f"请求失败: {response.status_code}")

# 遍历指定目录下的所有JSON文件
def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)
                table_name = os.path.basename(root)
                # 创建表
                cursor.execute(create_table_sql.format(table_name=table_name))
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # 判断数据格式
                    if isinstance(data, list):
                        for item in data:
                            process_item(item, table_name)
                    elif isinstance(data, dict):
                        process_item(data, table_name)
                    else:
                        print(f"无法处理的JSON格式: {json_file_path}")

# 处理指定目录下的所有JSON文件
directory_path = r"D:\MyLab\ZTB\ZJU_Calendar\LLM_Backend\spider1\spider1\result"
process_directory(directory_path)

# 提交事务并关闭连接
conn.commit()
conn.close()

print("数据已成功插入到SQLite数据库中。")