import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ValidationError
from fastapi.middleware.cors import CORSMiddleware
from spider1.main import run_all_crawlers
import threading
import logging
from utils.db import populate_database_from_json, SQLITE_DB_PATH
from milvus.local_qa import answer_question

# 配置日志
logging.basicConfig(level=logging.INFO)

# 在 FastAPI 应用启动前填充数据库, 下次一定
# populate_database_from_json()

# FastAPI 应用
app = FastAPI()

# 添加CORS中间件
origins = ["http://localhost:8081", "http://127.0.0.1:8081", "http://localhost:8082"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 定义 Pydantic 模型
class Notice(BaseModel):
    title: str
    date: str
    link: str
    content: str
class QuestionRequest(BaseModel):
    question: str

# SQLite 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect(SQLITE_DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/notices/{table_name}", response_model=list[Notice])
def read_notices(table_name: str, limit: int = 10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT title, date, link, content FROM {table_name} ORDER BY date DESC LIMIT ?", (limit,))
    notices = cursor.fetchall()
    conn.close()

    if not notices:
        raise HTTPException(status_code=404, detail="No notices found")

    validated_notices = []
    for notice in notices:
        try:
            validated_notices.append(Notice(**dict(notice)))
        except ValidationError as e:
            print(f"Validation error for notice: {notice}")
            print(e)
    return validated_notices

@app.get("/notices/{table_name}/{notice_id}", response_model=Notice)
def read_notice(table_name: str, notice_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT title, date, link, content FROM {table_name} WHERE id = ?", (notice_id,))
    notice = cursor.fetchone()
    conn.close()

    if notice is None:
        raise HTTPException(status_code=404, detail="Notice not found")

    try:
        return Notice(**dict(notice))
    except ValidationError as e:
        print(f"Validation error for notice: {notice}")
        print(e)
        raise HTTPException(status_code=400, detail="Invalid notice data")

@app.post("/run_crawlers")
def run_crawlers():
    try:
        # 使用线程运行爬虫，避免阻塞 FastAPI 的主线程
        def run_and_populate():
            run_all_crawlers()  # 运行爬虫
            populate_database_from_json()  # 在爬虫完成后填充数据库

        thread = threading.Thread(target=run_and_populate)
        thread.start()
        return {"message": "Crawlers started successfully and data will be inserted into the database upon completion."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask")
async def ask_question(request: QuestionRequest):
    question = request.question
    if not question:
        raise HTTPException(status_code=400, detail="Question is required.")
    
    try:
        answer = answer_question(question)  # 调用 answer_question 生成回答
        return {"question": question, "answer": answer}
    except Exception as e:
        print(f"Error processing question: {e}")
        raise HTTPException(status_code=500, detail="Error processing question.")
    
# 运行 FastAPI 应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)