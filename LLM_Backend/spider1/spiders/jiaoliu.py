import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

class UgrsSpider(scrapy.Spider):
    name = 'ugrs'
    allowed_domains = ['ugrs.zju.edu.cn']
    start_urls = ['https://ugrs.zju.edu.cn/dwjlfwpt/jsgx/list1.htm']
    counter = 1

    def __init__(self):
        self.base_url = 'https://ugrs.zju.edu.cn'
        self.today = datetime.now()
        self.three_months_ago = self.today - timedelta(days=90)
        self.result_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'result', 'jiaoliu'))
        os.makedirs(self.result_dir, exist_ok=True)

    def parse(self, response):
        notices = []

        # 查找并处理每个通知
        for notice in response.css('.cg-news-list li'):
            date_text = notice.css('.art-date::text').get()
            if date_text:
                date = datetime.strptime(date_text.strip(), '%Y-%m-%d')
                title = notice.css('a::attr(title)').get()
                link = notice.css('a::attr(href)').get()
                if link:
                    full_link = self.base_url + link
                    notices.append({'title': title, 'date': date, 'link': full_link})

        # 对日期进行排序
        notices.sort(key=lambda x: x['date'])

        # 判断最小日期是否小于有效日期
        if notices and notices[0]['date'] < self.three_months_ago:
            # 找到刚好大于有效日期的通知
            for notice in notices:
                if notice['date'] >= self.three_months_ago:
                    yield scrapy.Request(notice['link'], callback=self.parse_activity_page, meta={'title': notice['title'], 'date': notice['date'].strftime('%Y-%m-%d'), 'link': notice['link']})
        else:
            # 继续爬取下一页
            next_page = response.css('li.page_nav a.next::attr(href)').get()
            if next_page:
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
# process.crawl(UgrsSpider)
# process.start()