# ZJU_Calendar

## ����ǰ��
cd dayspan-frontend
npm install
npm run serve

## �������
cd LLM_Backend/server
cd LLM_Backend/milvus
docker-compose up -d 
python main.py

## ��������
cd LLM_Backend/spider1
python main.py

## ����ȡ���ı���json��coze_bot�����������ݿ�notices.db
cd LLM_Backend/utils
python llm_api.py

## ����milvus�������ݿ�
cd LLM_Backend/milvus
docker-compose up -d 
python local_qa.py


����2024��10������Щֵ�òμӵı�����
��������ѧ԰��ѧ������Ӧ�����׼�����ܻ���������ʵ���Ŷӵ�������
�㽭��ѧ���ں͹������Щ��ѧ�ж��⽻����������Щ�Ѿ���ʾ�������������ˣ�