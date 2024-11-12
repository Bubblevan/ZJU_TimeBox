import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

class LantianSpider(scrapy.Spider):
    name = 'lantian'
    allowed_domains = ['lantian.zju.edu.cn']
    start_urls = ['http://lantian.zju.edu.cn/ltoffice/20209/list.htm']
    counter = 1

    def __init__(self):
        self.stop_crawling = False
        self.base_url = 'http://lantian.zju.edu.cn'
        self.today = datetime.now()
        self.three_months_ago = self.today - timedelta(days=90)
        self.result_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'result', 'lantian'))
        os.makedirs(self.result_dir, exist_ok=True)

    def parse(self, response):
        if self.stop_crawling:
            return

        # 查找并处理每个通知
        notices = response.css('.news_list li')
        for notice in notices:
            date_text = notice.css('.news_meta::text').get()
            if date_text:
                date = datetime.strptime(date_text.strip(), '%Y-%m-%d')
                if date < self.three_months_ago:
                    self.stop_crawling = True
                    return
                title = notice.css('.news_title a::attr(title)').get()
                link = notice.css('.news_title a::attr(href)').get()
                if link:
                    full_link = self.base_url + link
                    yield scrapy.Request(full_link, callback=self.parse_activity_page, meta={'title': title, 'date': date_text, 'link': full_link})
        
        # 查找下一页链接并继续爬取
        next_page = response.css('li.page_nav a.next::attr(href)').get()
        if next_page and not self.stop_crawling:
            next_page_url = self.base_url + next_page
            yield scrapy.Request(next_page_url, callback=self.parse)

    def parse_activity_page(self, response):
        title = response.meta['title']
        date = response.meta['date']
        link = response.meta['link']
        content = self.extract_content(response.body)
        
        # 打印内容
        print(f'Title: {title}')
        print(f'Date: {date}')
        print(f'Link: {link}')
        print(f'Content: {content}')
        
        # 保存到单个JSON文件
        self.save_to_file({
            'title': title,
            'date': date,
            'link': link,
            'content': content
        })

    def extract_content(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        content_div = soup.find('div', class_='wp_articlecontent')
        if content_div:
            return self.clean_text(content_div)
        return ''

    def clean_text(self, element):
        for script in element(["script", "style"]):
            script.decompose()
        return ' '.join(element.stripped_strings)
    
    def save_to_file(self, data):
        filename = os.path.join(self.result_dir, f'content{self.counter}.json')
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.counter += 1

# 运行爬虫
# process = CrawlerProcess()
# process.crawl(LantianSpider)
# process.start()