# ZJU_Calendar

## 启动前端
cd dayspan-frontend
npm install
npm run serve

## 启动后端
cd LLM_Backend/server
cd LLM_Backend/milvus
docker-compose up -d 
python main.py

## 启动爬虫
cd LLM_Backend/spider1
python main.py

## 将爬取到的本地json经coze_bot精简后插入数据库notices.db
cd LLM_Backend/utils
python llm_api.py

## 启动milvus向量数据库
cd LLM_Backend/milvus
docker-compose up -d 
python local_qa.py


请问2024年10月有哪些值得参加的比赛？
我是蓝田学园的学生，我应该如何准备才能获得优秀社会实践团队的荣誉？
浙江大学近期和国外的哪些大学有对外交流合作，哪些已经公示名单结束报名了？