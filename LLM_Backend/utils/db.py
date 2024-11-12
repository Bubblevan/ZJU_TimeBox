import os
import sqlite3
import json
import logging

SQLITE_DB_PATH = '../notices.db'

# ������־
logging.basicConfig(level=logging.INFO)

# ���������� SQLite ���ݿ�
def get_db_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# �����ļ������ƴ�����
def create_table_if_not_exists(table_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            date TEXT,
            link TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logging.info(f"Table {table_name} created successfully.")

# �� JSON �ļ��������ݵ�ָ����
def insert_data_from_json_to_table(json_file_path, table_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    if isinstance(data, dict):
        data = [data]  # ��������ǵ����ֵ䣬����ת��Ϊ�б�

    for item in data:
        title = item.get("title")
        date = item.get("date")
        link = item.get("link")
        content = item.get("content")

        if title and date and link and content:
            cursor.execute(f'''
                INSERT INTO {table_name} (title, date, link, content)
                VALUES (?, ?, ?, ?)
            ''', (title, date, link, content))
        else:
            logging.warning(f"Skipping item due to missing fields: {item}")

    conn.commit()
    conn.close()
    logging.info(f"Data inserted into table {table_name} from file {json_file_path}.")

# �� result �ļ��ж�ȡ���ݲ��������ݿ�
def populate_database_from_json():
    result_dir = os.path.join(os.path.dirname(__file__), "../result")
    
    for folder_name in os.listdir(result_dir):
        folder_path = os.path.join(result_dir, folder_name)
        if os.path.isdir(folder_path):
            logging.info(f"Creating table for folder: {folder_name}")
            create_table_if_not_exists(folder_name)
            
            for file_name in os.listdir(folder_path):
                if file_name.endswith(".json"):
                    json_file_path = os.path.join(folder_path, file_name)
                    logging.info(f"Inserting data from file: {json_file_path} into table: {folder_name}")
                    insert_data_from_json_to_table(json_file_path, folder_name)