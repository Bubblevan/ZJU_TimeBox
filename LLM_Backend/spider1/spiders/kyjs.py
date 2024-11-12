import requests
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import os

def ensure_file_exists(file_path):
    if not os.path.exists(file_path):
        # 如果文件不存在，创建一个空文件
        file_path = os.path.abspath(file_path)
        print(f"Creating empty file: {file_path}")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=4)

def run_kyjs_crawler():
    # 定义请求的 URL
    list_url = "http://kyjs.zju.edu.cn/prod-api/home/news/page?pageNum=1&pageSize=22&position=2"

    # 定义请求的 headers
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Host": "kyjs.zju.edu.cn",
        "Referer": "http://kyjs.zju.edu.cn/more?type=10&title=%E9%87%8D%E7%82%B9%E6%8F%90%E7%A4%BA",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36 SLBrowser/9.0.3.5211 SLBChan/111"
    }

    # 发送 GET 请求获取通知列表
    response = requests.get(list_url, headers=headers)
    data = response.json()

    # 解析通知列表，获取每个通知的 newsId
    news_ids = [record['newsId'] for record in data['data']['records']]

    # 定义存储通知详情的列表
    news_details = []

    # 定义六个月前的时间
    six_months_ago = datetime.now() - timedelta(days=180)

    # 遍历 newsId，发送 GET 请求获取通知详情
    for news_id in news_ids:
        detail_url = f"http://kyjs.zju.edu.cn/prod-api/home/news/detail?newsId={news_id}"
        detail_response = requests.get(detail_url, headers=headers)
        detail_data = detail_response.json()
        
        # 解析通知详情中的时间
        publish_time = datetime.strptime(detail_data['data']['publishTime'], '%Y-%m-%d %H:%M:%S')
        
        # 如果通知时间超过六个月，停止爬取
        if publish_time < six_months_ago:
            break
        
        # 使用 BeautifulSoup 解析 content 并提取纯文本
        soup = BeautifulSoup(detail_data['data']['content'], 'html.parser')
        content_text = soup.get_text(separator='\n').strip()
        content_text = content_text.replace('\n', ' ')

        # 只保留 title、content 和 publishTime 字段，并添加原链接
        filtered_data = {
            "title": detail_data['data']['title'],
            "date": detail_data['data']['publishTime'],
            "link": detail_url,
            "content": content_text
        }
        
        # 将过滤后的通知详情添加到列表中
        news_details.append(filtered_data)

    # 确保文件存在
    file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../result/kyjs/kyjs.json'))
    ensure_file_exists(file_path)

    # 将通知详情存储到本地 JSON 文件
    print(f"Writing data to: {file_path}")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(news_details, f, ensure_ascii=False, indent=4)

    print("通知详情已存储到 kyjs.json 文件中。")

if __name__ == "__main__":
    run_kyjs_crawler()