import os
import json
import sqlite3
import requests

# ���� API �� URL �� API ��Կ
API_URL = "https://api.coze.cn/v3/chat"
API_KEY = "pat_lh9minUw0dYuu6QHFIq7rz1kY6tkFv70Iiic766T3IGNn2PuxxZijAGdOh9ZFknb"

# ����ͷ
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ���ӵ�SQLite���ݿ�
db_path = r"D:\MyLab\ZTB\ZJU_Calendar\LLM_Backend\spider1\notices.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# �������SQLģ��
create_table_sql = '''
CREATE TABLE IF NOT EXISTS {table_name} (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    date TEXT,
    link TEXT,
    content TEXT
)
'''

# �������Ƿ��Ѵ��ڵ�SQLģ��
check_title_sql = '''
SELECT COUNT(*) FROM {table_name} WHERE title = ?
'''

# �������ݵ�SQLģ��
insert_data_sql = '''
INSERT INTO {table_name} (title, date, link, content)
VALUES (?, ?, ?, ?)
'''

# ����ÿ����Ŀ
def process_item(item, table_name):
    # ����content�ֶ�
    payload = {
        "bot_id": "7435604864455442486",
        "user_id": "123123",
        "stream": True,
        "auto_save_history": True,
        "additional_messages": [
            {
                "role": "user",
                "content": f"������������,�����ؼ���Ϣ(�����ǿ�ʼ�ͽ���ʱ��)��{item['content']}.���ûش���Ҳ�������ԭ��,ֱ�����120�����ھ�����һ�λ�,��Ҫ�ֵ�.���content����Ϊ��,ֱ�ӷ���@@@",
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
                            print("�Ի���ʷ:", json_data)
                    except json.JSONDecodeError:
                        print("�޷���������Ӧ��:", decoded_line)
        
        # ������������ݲ���@@@������뵽SQLite���ݿ�
        if simplified_content != "@@@":
            # �������Ƿ��Ѵ���
            cursor.execute(check_title_sql.format(table_name=table_name), (item['title'],))
            if cursor.fetchone()[0] == 0:
                cursor.execute(insert_data_sql.format(table_name=table_name), (item['title'], item['date'], item['link'], simplified_content))
    else:
        print(f"����ʧ��: {response.status_code}")

# ����ָ��Ŀ¼�µ�����JSON�ļ�
def process_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".json"):
                json_file_path = os.path.join(root, file)
                table_name = os.path.basename(root)
                # ������
                cursor.execute(create_table_sql.format(table_name=table_name))
                with open(json_file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    # �ж����ݸ�ʽ
                    if isinstance(data, list):
                        for item in data:
                            process_item(item, table_name)
                    elif isinstance(data, dict):
                        process_item(data, table_name)
                    else:
                        print(f"�޷������JSON��ʽ: {json_file_path}")

# ����ָ��Ŀ¼�µ�����JSON�ļ�
directory_path = r"D:\MyLab\ZTB\ZJU_Calendar\LLM_Backend\spider1\spider1\result"
process_directory(directory_path)

# �ύ���񲢹ر�����
conn.commit()
conn.close()

print("�����ѳɹ����뵽SQLite���ݿ��С�")